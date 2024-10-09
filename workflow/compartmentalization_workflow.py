# Import general modules for deepcopies, timetracking, and dumping results
import copy
import datetime
import time
import pickle

# Pandas used for Q-table lookups
import pandas as pd

# Workflow modules
from module_compartmentalization import CompartmentalizationModule
from module_phenomena import PhenomenaModule
from module_assembler import AssemblerModule
from equation_workflow import EquationGenerator
from module_input import InputModule
from object_library import *

# Some dependencies generated annoying warnings, ignored
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

class Workflow():

    def run_workflow(self, 
                     episodes: int,
                     epsilon: float,
                     r_alloc: str,
                     r_shape: str,
                     LL_multilearning: str,
                     LL_iter: int,
                     LL_eps: float,
                     case_study: str,
                     modus: str,
                     Q) -> dict:

        # Begin to track time for quantitative evaluation
        start_time = time.time()

        # In the phenomena module we define the constitutive equations, and structure them in dictionaries to be used in the lower-level equation generator
        phenomena_module = PhenomenaModule()
        phenomena = phenomena_module.get_phenomena(case_study, modus)

        # Generate a dictionary to store all results of the workflow run
        results_dict = {}
        
        # Create an empty Q-table, or use supplied Q-table if given (transfer learning)
        if isinstance(Q,int):
            Q = pd.DataFrame(columns=["state", "action", "noofvisits", "R_tot", "Q(s,a)"]) # If a state-action pair is the last in a trajetory, the last column specifies the number of the trajectory, otherwise contains "None".
        else:
            Q = Q

        # Dummy initialization of a Q-table if we use the same Q-table for each lower-level run (not safe at the moment)
        Q_eq_learned = 0

        # Initialization of reward tracker
        overall_best_reward = -9999
        reward_tracker = []

        # Find optimal model through reinforcement learning
        ## One episode corresponds to a series of upper-level graph manipulations, whose combined rewards are processed and only then transferred to the Q-table (like a batch in batch-RL, see thesis)
        for e in range(episodes):
            print("Episode: " + str(e))

            # The compartmentalization module hosts the graph manipulation rules as well as methods to initialize the graphs and actually perform the manipulation step
            compm = CompartmentalizationModule()

            # The building blocks are the subunits of the model, and each model compartment and interface extends one of these general classes (CSTR, PFR...)
            building_blocks = get_building_blocks(case_study)

            # Initialize the topology based on the input and building blocks
            compm.initialize_topology(case_study, building_blocks, modus)

            # Reset iteration counter for new episode
            it = 0

            # Collect all rewards from within this episode/trajectory so that it can be processed later via the "AVERAGE" or "BEST" strategies (see thesis)
            trajectory_reward = []

            # Reset of episode reward tracker
            episode_best_reward = -9999
            episode_best_model = None

            # In each episode, perform multiple iterations of applying a action (the graph manipulation) to the state (the graph/model)
            while compm.topology.completed == False:
                it += 1

                # Get all actions that are possible in the current state
                available_actions = []
                available_actions = compm.get_actions(it, case_study)

                # Choose action from the available one 
                chosen_action = compm.choose_action(epsilon, available_actions, Q)

                # Before action is applied, record current state and chosen action (state-action pair) in current_trajectory
                compm.current_trajectory.append([copy.deepcopy(compm.topology.canonical_form), chosen_action])
                # Apply step to current state
                compm.step(chosen_action, modus)
                
                # The assembler executes various tasks to translate the model graph to a set of equations
                assembler = AssemblerModule(compm.topology, phenomena)

                assembler.clean_topology()
                assembler.assign_phenomena(modus)
                assembler.generate_state(modus)
                assembler.trace_volume(modus)
                assembler.generate_eqlib(modus)

                # Take the input values (known parameters, experimental values...) and prepare them so that the lower-level equation generator can integrate them in the assembled model equations
                input_module = InputModule()
                input_profile = input_module.generate_input_profile(case_study, modus)
                assembler.generate_knownvals(input_profile, modus)
                
                # From the assembler, get everything needed for the equation generator
                initial_state = assembler.state
                eq_library = assembler.eq_library
                exclusive_eqs = assembler.exclusive_eqs
                known_values = assembler.known_values

                # Show current graph after assembler (halts program until Jaal window is closed)
                # assembler.topology.print_to_jaal()

                # Initialize the equation generator
                equation_generator = EquationGenerator()

                # Choose reward shaping strategy
                ## "ACC" is the purely accuracy-based one
                if r_shape == "ACC":
                    reward_shaping = 0
                ## Every outgoing stream must have something happen to it (useful for PTC case study as both phases are always consideren then)
                if r_shape == "NOLOOP":
                    reward_shaping = - 1 * len([interface for interface in assembler.topology.interfaces if interface.compartment_from == interface.compartment_to])
                ## Rest is self-explanatory
                if r_shape == "MUSTREACTION":
                    reward_shaping = -1 * (not any([isinstance(comp,CSTR) for comp in assembler.topology.compartments]))
                if r_shape == "MUSTMT":
                    reward_shaping = -1 * (not any([isinstance(intf,FILM) for intf in assembler.topology.interfaces]))
                if r_shape == "NOLOOP+MUSTMT":
                    reward_shaping = - 1 * len([interface for interface in assembler.topology.interfaces if interface.compartment_from == interface.compartment_to]) - 1 * (not any([isinstance(intf,FILM) for intf in assembler.topology.interfaces]))
                if r_shape == "NOMIX":
                    reward_shaping = - 1 * (any([isinstance(comp,MIX) for comp in assembler.topology.compartments]))
                if r_shape == "REACTION+MT5":
                    reward_shaping = 0.5 * (any([isinstance(comp,CSTR) for comp in assembler.topology.compartments])) + 0.5 * (any([isinstance(interface,FILM) for interface in assembler.topology.interfaces]))
                if r_shape == "REACTION+MT2":
                    reward_shaping = 0.2 * (any([isinstance(comp,CSTR) for comp in assembler.topology.compartments])) + 0.2 * (any([isinstance(interface,FILM) for interface in assembler.topology.interfaces]))
                if r_shape == "NOLOOP+REACTION+MT+NOMIX":
                    reward_shaping = - 0.5 * (any([isinstance(comp,MIX) for comp in assembler.topology.compartments])) + 0.5 * (any([isinstance(comp,CSTR) for comp in assembler.topology.compartments])) + 0.5 * (any([isinstance(interface,FILM) for interface in assembler.topology.interfaces])) - 1 * len([interface for interface in assembler.topology.interfaces if interface.compartment_from == interface.compartment_to])

                # Filter out graphs that achieve a negative knowledge-based reward by setting their amount equation generation episodes to 0
                e_equation_gen = 0
                if reward_shaping > -0.01:
                    # If graph achieves knowledge-based accuracy > -0.01, give it the full desired amount of lower-level episodes
                    e_equation_gen = LL_iter

                # Hyperparameter to integrate Q-table of all lower-level runs (not safe)
                if LL_multilearning == "off":
                    Q_eq_learned = 0 
                
                # If topology is not filtered out, perform equation generation to fully specify model
                if e_equation_gen > 0:
                    current_model_name, current_trajectory_reward, current_solved_model, Q_eq_learned, current_model_state = equation_generator.run_workflow(initial_state, 
                                                                                                                                        known_values, 
                                                                                                                                        eq_library,
                                                                                                                                        exclusive_eqs,
                                                                                                                                        e_equation_gen,
                                                                                                                                        LL_eps,
                                                                                                                                        assembler.topology,
                                                                                                                                        Q_eq_learned,
                                                                                                                                        compm.current_trajectory,
                                                                                                                                        modus
                                                                                                                                        )
                else:
                    current_model_name = "no_model_generated"
                    current_trajectory_reward = 0
                    current_solved_model = None
                    current_model_state = []

                # Keep track of (best) rewards
                current_accuracy_reward = current_trajectory_reward
                print("Accuracy Reward: " + str(current_accuracy_reward))
                current_trajectory_reward += reward_shaping
                print("Model Reward: " + str(current_trajectory_reward) + "\n")

                reward_tracker.append(current_trajectory_reward)

                if current_trajectory_reward > episode_best_reward:
                    episode_best_reward = current_trajectory_reward
                    episode_best_accuracy = current_accuracy_reward
                    episode_best_model = copy.deepcopy(assembler.topology)
                    episode_best_model_name = current_model_name
                    episode_best_model_solution = copy.deepcopy(current_solved_model)
                    episode_best_model_state = current_model_state

                if current_trajectory_reward > overall_best_reward:
                    overall_best_reward = current_trajectory_reward
                    overall_best_accuracy = current_accuracy_reward
                    overall_best_model = copy.deepcopy(assembler.topology)
                    overall_best_model_name = current_model_name
                    overall_best_model_solution = copy.deepcopy(current_solved_model)
                    overall_best_model_state = current_model_state

                trajectory_reward.append(current_trajectory_reward)

                # Terminate run if good model is found (was enabled for CS1 quantitative evaluation)
                # if overall_best_accuracy > 0.9:
                #     compm.topology.completed = True

            # Reward allocation strategies as described in thesis
            if r_alloc == "AVERAGE":
                # Average over all next steps
                for index1, reward1 in enumerate(trajectory_reward):
                    for index2, reward2 in enumerate(trajectory_reward):
                        if index2 > index1:
                            trajectory_reward[index1] += trajectory_reward[index2]
                    trajectory_reward[index1] /= len(trajectory_reward) - index1

            if r_alloc == "BEST":
                ## Best following step
                for index1, reward1 in enumerate(trajectory_reward):
                    for index2, reward2 in enumerate(trajectory_reward):
                        if index2 > index1:
                            if reward2 > trajectory_reward[index1]:
                                trajectory_reward[index1] = trajectory_reward[index2]

            print("Episode Rewards: " + str(trajectory_reward))
            print("\n")

            # Update Q-table of topology generation
            for i, (state, action) in enumerate(compm.current_trajectory):  # Unpack directly in the loop
                # Find tuple in Q table
                match_condition = (Q["state"] == state) & (Q["action"] == action)
                
                if not match_condition.any():
                    copied_state = copy.deepcopy(state)  # Deep copy the state to avoid later alterations
                    new_row_in_Q = pd.DataFrame([{
                        "state": copied_state,
                        "action": action,
                        "noofvisits": 0.0,
                        "R_tot": 0.0,
                        "Q(s,a)": -99
                    }])
                    Q = pd.concat([Q, new_row_in_Q], ignore_index=True)
                    match_condition = (Q["state"] == state) & (Q["action"] == action)
                
                # Update the number of visits and total reward
                Q.loc[match_condition, "noofvisits"] += 1
                Q.loc[match_condition, "R_tot"] += trajectory_reward[i]
                current_Q_value = Q.loc[match_condition, "Q(s,a)"].values[0]
                
                # Update Q(s,a) to the trajectory_reward if it's greater than the current Q value
                if trajectory_reward[i] > current_Q_value:
                    Q.loc[match_condition, "Q(s,a)"] = trajectory_reward[i]

                # Constructs a human-readable Q-table for debugging
                Q_readable = copy.deepcopy(Q)
                Q_readable["action"] = Q_readable["action"].apply(lambda x: str(x))
            
            # Collect current episode's results
            results_dict[e] = {
                'best_model_filename': episode_best_model_name,
                'best_topology': episode_best_model,
                'jaal_info': episode_best_model.print_to_jaal(False) if episode_best_model is not None else None,
                'trajectory_reward': episode_best_reward,
                'accuracy_reward': episode_best_accuracy,
                'is_good': False,
                'is_best': False,
                'num_iterations': it
            }

            # Terminate run if good model is found (was enabled for CS1 quantitative evaluation)
            # if overall_best_accuracy > 0.9:
            #     break

        # Time tracking
        end_time = time.time()
        duration = end_time - start_time
        
        # Label good / best models for easier identification later
        for e in results_dict:
            if results_dict[e]["best_model_filename"] == overall_best_model_name:
                results_dict[e]["is_best"] = True
            if results_dict[e]["trajectory_reward"] > 0.9:
                results_dict[e]["is_good"] = True

        # Save Q-table for transfer learning
        results_dict["Q"] = Q

        # Clean result_dict for pickling (phenomena allocation function cannot be pickled)
        for e in results_dict.keys():
            if e != "Q":
                for comp in results_dict[e]['best_topology'].compartments:
                    for phenomenon in comp.phenomena:
                        phenomenon.generate_eqlib = ""
                for interf in results_dict[e]['best_topology'].interfaces:
                    for phenomenon in interf.phenomena:
                        phenomenon.generate_eqlib = ""

        # Dump results in pickle file
        results_file = open('./workflow/outputs/results/results_' + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), 'xb')
        pickle.dump(results_dict, results_file)                    
        results_file.close()

        # Show best model topology graph (halts program until Jaal window is closed)
        overall_best_model.print_to_jaal()
        
        # Print out selected variables values from best model for debugging
        # var_values = {}
        # if overall_best_model_solution is not None:
        #     for v in overall_best_model_solution.component_objects(pyo.environ.Var, active=True):
        #         if "environment" in str(v):
        #             var_object = getattr(overall_best_model_solution, str(v))
        #             for index in var_object:
        #                 var_values[str(v) + str(index)] = var_object[index].value

        return results_dict, duration