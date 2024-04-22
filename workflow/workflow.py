import copy
import datetime
import json

import pandas as pd

from module_input import InputModule
from module_compartmentalization import CompartmentalizationModule
from module_library import LibraryModule
from module_equation_generator import EquationGeneratorModule
from module_parser import ParserModule
from module_solver_parmest import SolverParmestModule
from module_postprocessing import PostprocessingModule


class Workflow():

    def run_workflow(self, 
                     workflow_modus: str,
                     episodes: int,
                     training_policy: str,
                     epsilon: float,
                     max_epsilon: float,
                     reward_policy: str,
                     updating_policy: str,
                     case_study: str,
                     data_size: str,
                     noise: str) -> dict:

        """Run workflow

        Run workflow by instantiating the modules (input module, compart. module,
        equation generation module, library module, parser module, solver/parmest
        module, postprocessing module) and putting them to use one after the other.
        
        Parameter:
            workflow_modus (str):
                Determines how the workflow is executed. Choose from:
                "modus-normal" (not fully implemented),
                "modus-reduced-model-space",
                "modus-reduced-model-space-learning-curves",
                "modus-explore-reduced-model-space". 
                See documentation for details.
            
            episodes (int):
                Number of iterations of the reinforcement learning process.
                Corresponds to number of models (= number of complete
                state-action trajectories) to build.

            training_policy (str):
                Policy that determines how exploration and exploitation is
                balanced during training. Choose from "eps-greedy-static",
                "eps-greedy-dynamic", "trainingpolicy-3" (not fully
                implemented), "trainingpolicy-4" (not fully implemented).

            epsilon (float):
                Only used for training_policy == "eps-greedy-static". Sets
                the epsilon used. Choose between [0,1]. Low favors
                exploitation, high favors exploration.

            max_epsilon (float):
                Only needed if trainings policy is "eps-greedy-dynamic".
                Usually 1. Epsilon linearly decreases to 0 from the
                specified value. 

            reward_policy (str):
                Determines applied policy for computing the reward from
                accuracy, solvability, and complexity of the model. Choose
                from: "no-complexity-penalty", "with-complexity-penalty".

            updating_policy (str):
                Determines how values in the Q-table are computed. Choose
                from: "averaging" (average reward of all trajectories
                through the given state-action pair).

            case_study (str):
                Determines the data source. Choose from: "cs-insilico",
                "cs-experimental".

            data_size (str):
                Determines the number of data points that should be used.
                For "cs-insilico" choose from: "21-pts". For
                "cs-experimental" choose from: "7-pts".

            noise (str):
                Determines whether noise is added to the experimental data.
                This is used to test the robustness of the workflow. For
                "cs-insilico" choose from: "no-noise". For
                "cs-experimental" choose from: -.

        Returns:
            results_dict (dict):
                For each episode contains the filename, accuracy, reward, and state-
                action trajectory of the generated model. Also contains all parameters 
                that were fitted and a snap-shot of the Q-table at the end of each episode.
        """

        with open('workflow/reduced_search_space_trajectories.json', 'r') as json_file:
            reduced_search_space_trajectories = json.load(json_file)

        # Instantiate all modules besides the equation_generator_module which is 
        # freshly instantiated for each episode
        input_module = InputModule()
        compartmentalization_module = CompartmentalizationModule()
        library_module = LibraryModule()
        parser_module = ParserModule()
        solver_parmest_module = SolverParmestModule()
        postprocessing_module = PostprocessingModule()

        # Generate input profile
        input_profile = input_module.generate_input_profile(case_study, data_size, noise)

        # Generate model compartmentalization (currently not implemented, instead assumes a single 1D compartment)
        _ = compartmentalization_module.generate_topology()

        # Generate a dictionary to store all results of the workflow run
        results_dict = {}
        
        # Create an empty Q-table
        Q = pd.DataFrame(columns=["state", "action", "noofvisits", "R_tot", "Q(s,a)", "terminalOfTrajectoryNo"]) # If a state-action pair is the last in a trajetory, the last column specifies the number of the trajectory, otherwise contains "None".

        # Find optimal model through reinforcement learning
        for e in range(episodes):  # An episode corresponds to building one fully specified model, parsing it to pyomo code, fitting parameters, determining model accuracy and updating the Q-table.
            # Create a fresh initial state that will be altered until each term is decided, then it is parsed into Pyomo code. Create library with equations where the nodes/elements point to same objects as the state, i.e., if a variable is declared neglected in the state it is also declared neglected in all constitutive equations right away.
            initial_state, eq_library = library_module.generate_initial_state_and_lib()   
            
            # Create environment of this episode. The env object holds the state, the input profile and the equation library. It possesses the methods/functions to alter/specify the state into a fully defined system of equations.
            env = EquationGeneratorModule(initial_state, input_profile, eq_library)     

            # Define auxiliary variables
            r = 0  # Needed for "modus-explore-reduced-model-space", counts at which state-action pair in trajectory the workflow is.
            trajectory_terminated = False # Is returned by env.step and turns True if trajectory terminates after current state.
            
            # In each episode iterate through state and make decision for first undecided term until all decisions are made (trajectory_terminated == True)
            while trajectory_terminated == False:
                
                # GET NAME OF FIRST UNDECIDED SYMBOLIC VARIABLE IN THE STATE (This is the variable that is decided in this iteration.)    
                current_undecided_symbolic_node = env.get_current_undecided_symbolic_node() # returns name (i.e., attribute "unique_representation") of first term in state that is still "undecided"

                # GET AVAILABLE ACTIONS for the current state, i.e., available actions for the first "undecided" node in the state
                if workflow_modus == "modus-normal":
                    # (1) For normal operation:
                    # available_actions = env.get_actions() # Not fully implemented. ToDo: only call this method if there is at least one undecided node
                    pass
                elif workflow_modus == "modus-explore-reduced-model-space":
                    # (2) For testing manually created reduced search space trajectories one by one.
                    available_actions = [reduced_search_space_trajectories[str(e)][r]]
                    r += 1
                elif workflow_modus in ["modus-reduced-model-space", "modus-reduced-model-space-learning-curves"]:
                    # (3) For returning next available actions in those trajectories that coincide with current trajectory
                    action_trajectory = [sublist[1] for sublist in env.current_trajectory] # List of previously taken actions in current trajectory is the second column in current_trajectory (which saves the states in the first and the actions in the second column)
                    available_actions = env.get_actions_reduced_space(reduced_search_space_trajectories, action_trajectory)

                # APPEND ALL AVAILABLE STATE-ACTION PAIRS TO Q TABLE IF THEY ARE NOT YET INCLUDED
                for action in available_actions:
                    bool_state_match = Q["state"].apply(lambda x: x == env.state) # returns indices of Q's rows with current state
                    bool_action_match = Q["action"].apply(lambda x: x == action) # returns indices of Q's rows with current actions
                    bool_list = [state_match and action_match for state_match, action_match in zip(bool_state_match, bool_action_match)] # returns indices of Q's rows with current state AND action (Is state-action pair already included in Q?)
                    if not any(bool_list):
                        copied_state = copy.deepcopy(env.state) # Write a copy of the state-object to the Q table, so that it is not altered later on.
                        new_row_in_Q = pd.DataFrame([{"state": copied_state, "action": action, "noofvisits": float(0), "R_tot": float(0), "Q(s,a)": float(0.5), "terminalOfTrajectoryNo": None}]) # Note how Q(s,a) is initialized with 0.5.
                        Q = pd.concat([Q, new_row_in_Q], ignore_index=True) 

                # CHOOSE ACTION USING A TRAINING POLICY 
                chosen_action = env.choose_action(training_policy, epsilon, max_epsilon, e, available_actions, Q)  # Implement here, if we want to give certain actions priority (e.g., always take values from the problem profile if there are some available)

                # APPLY CHOSEN ACTION AND GET NEW STATE. 
                env.current_trajectory.append([copy.deepcopy(env.state), chosen_action]) # Before action is applied, record current state and chosen action (state-action pair) in current_trajectory. Keeps track of current trajectory (of state-action pairs) to distribute rewards to the visited state-action pairs. Deepcopy so that state objects are not altered later.
                trajectory_terminated, model_state = env.step(chosen_action) # The new state is written to the "state" variable of the env and also returned here. If this step terminates the trajectory: trajectory_terminated == True.

            # For result representation, find which of the predefined trajectories (i.e., models) was chosen.
            if workflow_modus in ["modus-reduced-model-space", "modus-explore-reduced-model-space", "modus-reduced-model-space-learning-curves"]:
                episodes_action_trajectory = [sublist[1] for sublist in env.current_trajectory]
                found_trajectory_key = None
                for trajectory_ID, trajectory_list_of_actions in reduced_search_space_trajectories.items(): # trajectory ID and list of actions in that trajectory
                    if trajectory_list_of_actions == episodes_action_trajectory:
                        found_trajectory_key = trajectory_ID
                        break

            # PARSE STATE TO MODEL, SOLVE MODEL ITERATIVELY TO FIND BEST PARAMETERS (Parmest package)
            # Once trajectory has terminated, i.e., no undecided nodes remain so that a fully specified model was created, perform parsing to output_model_filename and iterative solving/parameter estimation for DAE to obtain reward.
            output_model_filename = "generated_model_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_e" + str(e) + "_t" + str(found_trajectory_key) + ".py"
         
            try:
                # Parse terminal state to pyomo code
                output_model_filepath = "./workflow/outputs/generated_models/" + output_model_filename
                model_filepath, theta_names = parser_module.parse_model_to_file(model_state, input_profile, output_model_filepath) # Returns list of parameters that shall be fitted and stores model at output_model_filepath location

                # Estimate parameters in pyomo model by solving iteratively
                output_model_filepath = "outputs.generated_models." + output_model_filename
                trajectory_sse, theta = solver_parmest_module.find_optimal_params_and_solve_model(input_profile, theta_names, output_model_filepath)
            except Exception as ex:
                print(f"An exception occurred: {ex}")
                trajectory_sse = ex
                theta = ex

            # COMPUTE REWARD FOR TRAJECTORY
            # Once trajectory has terminated, compute reward of trajectory. 
            if isinstance(trajectory_sse, Exception): # For failed model executions and parameter fitting, give little reward (0.1) instead of no reward (0) to avoid overly large changes to Q table.
                trajectory_reward = 0.1 
            else: # For successful model execution and parameter fitting:
                if reward_policy == "no-complexity-penalty": 
                    # Reward computation after Petersen, 2021. Rewards are between 0 and 1. But they use NRMSE.
                    trajectory_reward = 1/(1+trajectory_sse)
                elif reward_policy == "with-complexity-penalty":
                    # Reward computation after Bassanne, 2019. Penalizes complexity. Rewards are roughly between 0 and 1. But they use RSE. 
                    ep1 = 1
                    ep2 = 0.125 # Chosen based on average state length so that rewards still remain around 1 or lower.
                    trajectory_reward = 1/(ep1+trajectory_sse) + 1/(ep2 * len(env.state))

            # UPDATE Q-TABLE
            # Update Q-table according to updating policy
            if updating_policy == "averaging":
                for i, tupel in enumerate(env.current_trajectory): # for each state-action tuple along trajectory
                    # Find tupel in Q table
                    bool_state_match = Q["state"].apply(lambda x: x == tupel[0])
                    bool_action_match = Q["action"].apply(lambda x: x == tupel[1])
                    bool_list = [state_match and action_match for state_match, action_match in zip(bool_state_match, bool_action_match)]
                    
                    # Update Q value
                    Q.loc[bool_list, "noofvisits"] += 1
                    Q.loc[bool_list, "R_tot"] += trajectory_reward
                    Q.loc[bool_list, "Q(s,a)"] = Q.loc[bool_list, "R_tot"] / Q.loc[bool_list, "noofvisits"]
                    
                    if workflow_modus in ["modus-reduced-model-space", "modus-explore-reduced-model-space", "modus-reduced-model-space-learning-curves"]:
                        # Add the trajectory number to those rows in Q that represent a terminal state-action pair (the end of a trajectory, a fully speciied model).
                        if i == len(env.current_trajectory) - 1: # in the last iteration, i.e., the terminal Q value, add the trajectory number. I.e., terminal state-action pairs (= models, full trajectories, note that last state is not included) are marked and we know their Q value.
                            Q.loc[bool_list, "terminalOfTrajectoryNo"] = found_trajectory_key

            
            # COLLECT RESULTS
            results_dict[e] = {
                'model_filename': output_model_filename,
                'trajectory_sse': trajectory_sse,
                'trajectory_reward': trajectory_reward,
                'trajectory_id': found_trajectory_key, # Exclude this if workflow_modus not in ["modus-reduced-model-space", "modus-explore-reduced-model-space", "modus-reduced-model-space-learning-curves"]
                'fitted_parameter(s)': ', '.join(f'{index}: {value}' for index, value in zip(theta.index.tolist(), theta.tolist())),
                #'action_trajectory': episodes_action_trajectory, # Exclude this if save_results_dictionary == True
                #'state_action_trajectory': env.current_trajectory, # Exclude this if save_results_dictionary == True
                #'Q_table': copy.deepcopy(env.state) # Exclude this if save_results_dictionary == True
            }

            if workflow_modus == "modus-reduced-model-space-learning-curves":
                # Once perfect model (trajectory key "0") is found, record number of iterations needed and proceed to next experiment.
                if found_trajectory_key == "0":
                    break # proceed to next workflow run
       

        # Apply postprocessing steps (currently no steps implemented)
        _ = postprocessing_module.apply_postprocessing()

        return results_dict


