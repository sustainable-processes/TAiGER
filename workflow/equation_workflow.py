import copy
import datetime
import pickle

import pandas as pd

from module_input import InputModule
from module_equation_generator import EquationGeneratorModule
from module_parser import ParserModule
from module_solver_parmest import SolverParmestModule
from module_postprocessing import PostprocessingModule
from classes_state_representation import get_og_info, reset_state
from module_assembler import AssemblerModule
from module_phenomena import PhenomenaModule

class EquationGenerator():

    def run_workflow(self,
                     initial_state,
                     input_profile,
                     eq_library, 
                     exclusive_eqs,
                     episodes: int,
                     epsilon: float,
                     topology,
                     Q_learned,
                     current_trajectory,
                     modus
                     ) -> dict:

        parser_module = ParserModule()
        solver_parmest_module = SolverParmestModule()

        debug_traj = current_trajectory ## DEBUG
        
        # Generate a dictionary to store all results of the workflow run
        results_dict = {}
        
        # Create an empty Q-table
        if isinstance(Q_learned,int):
            Q = pd.DataFrame(columns=["state", "action", "noofvisits", "R_tot", "Q(s,a)"])
        else:
            Q = Q_learned

        # Find optimal model through reinforcement learning
        current_best = -9999

        og_info = get_og_info(initial_state, eq_library)

        for e in range(episodes): 
            
            reset_state(og_info, initial_state, eq_library)
            env = EquationGeneratorModule(initial_state, input_profile, eq_library, exclusive_eqs, topology)

            # Set statuses of variables that are measurement quantities or that are manipulated over one or multiple experiments
            env.assign_measurement_quantities(modus)

            trajectory_terminated = False
            index_problem = False
            
            while trajectory_terminated == False:
                
                # GET NAME OF FIRST UNDECIDED SYMBOLIC VARIABLE IN THE STATE (This is the variable that is decided in this iteration.)    
                current_undecided_symbolic_node = env.get_current_undecided_symbolic_node() # returns name (i.e., attribute "unique_representation") of first term in state that is still "undecided"
                                    
                # GET AVAILABLE ACTIONS for the current state, i.e., available actions for the first "undecided" node in the state
                available_actions = env.get_actions_reduced_space()
                if available_actions == []:
                    trajectory_terminated = True
                    index_problem = True
                    break

                # CHOOSE ACTION USING A TRAINING POLICY 
                chosen_action = env.choose_action(epsilon, available_actions, Q)  

                # APPLY CHOSEN ACTION AND GET NEW STATE. 
                env.current_trajectory.append([copy.deepcopy(env.state), chosen_action]) # Before action is applied, record current state and chosen action (state-action pair) in current_trajectory. Keeps track of current trajectory (of state-action pairs) to distribute rewards to the visited state-action pairs. Deepcopy so that state objects are not altered later.
                
                env.assign_measurement_quantities(modus)
                
                trajectory_terminated, model_state = env.step(chosen_action) # The new state is written to the "state" variable of the env and also returned here. If this step terminates the trajectory: trajectory_terminated == True.

            # PARSE STATE TO MODEL, SOLVE MODEL ITERATIVELY TO FIND BEST PARAMETERS
            output_model_filename = "generated_model_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_e" + str(e) + ".py"

            
            if not index_problem:

                # Parse terminal state to pyomo code
                output_model_filepath = "./workflow/outputs/generated_models/" + output_model_filename
                model_filepath, theta_names = parser_module.parse_model_to_file(model_state, input_profile, output_model_filepath, modus) # Returns list of parameters that shall be fitted and stores model at output_model_filepath location

                try:
                    # Estimate parameters in pyomo model by solving iteratively
                    output_model_filepath = "outputs.generated_models." + output_model_filename
                    trajectory_sse, solved_model = solver_parmest_module.find_optimal_params_and_solve_model(input_profile, theta_names, output_model_filepath, 'baron', modus)
                except Exception as ex:
                    print(f"An exception occurred: {ex}")
                    trajectory_sse = ex
                    solved_model = ex

                # COMPUTE REWARD FOR TRAJECTORY
                if isinstance(trajectory_sse, Exception): 
                    trajectory_reward = -1
                else: 
                    trajectory_reward = 1/(1+trajectory_sse)

            else:
                # The equation generator runs into an error when it cannot assign a constitutive function or parameter to every symbol
                trajectory_reward = -0.8
                trajectory_sse = "index_problem"
                solved_model = "index_problem"

            # UPDATE Q-TABLE
            for i, tupel in enumerate(env.current_trajectory): # for each state-action tuple along trajectory
                # Find tupel in Q table
                bool_state_match = Q["state"].apply(lambda x: x == tupel[0])
                bool_action_match = Q["action"].apply(lambda x: x == tupel[1])
                bool_list = [state_match and action_match for state_match, action_match in zip(bool_state_match, bool_action_match)]

                if not any(bool_list):
                    copied_state = copy.deepcopy(tupel[0]) # Write a copy of the state-object to the Q table, so that it is not altered later on.
                    new_row_in_Q = pd.DataFrame([{"state": copied_state, "action": tupel[1], "noofvisits": float(0), "R_tot": float(0), "Q(s,a)": float(0)}]) # Note how Q(s,a) is initialized with 0.5.
                    Q = pd.concat([Q, new_row_in_Q], ignore_index=True)
                    
                    bool_state_match = Q["state"].apply(lambda x: x == tupel[0])
                    bool_action_match = Q["action"].apply(lambda x: x == tupel[1])
                    bool_list = [state_match and action_match for state_match, action_match in zip(bool_state_match, bool_action_match)]

                # Update Q value
                Q.loc[bool_list, "noofvisits"] += 1
                Q.loc[bool_list, "R_tot"] += trajectory_reward
                Q.loc[bool_list, "Q(s,a)"] = Q.loc[bool_list, "R_tot"] / Q.loc[bool_list, "noofvisits"]
            
            Q_readable = copy.deepcopy(Q)
            Q_readable["action"] = Q_readable["action"].apply(lambda x: str(x))

            # COLLECT RESULTS
            if not isinstance(trajectory_sse,float):
                trajectory_sse = "Error"
                solved_model = "Error"

            results_dict[e] = {
                'model_filename': output_model_filename,
                'trajectory_sse': trajectory_sse,
                'trajectory_reward': trajectory_reward,
                # 'kinetic_constant': solved_model.ap_reaction_k.value,
                # 'kinetic_order': solved_model.ap_reaction_ord_i
            }

            if modus == "hierarchic_data":
                results_dict[e] |= {
                    'kinetic_constant': solved_model.ap_reaction_k.value,
                    'kinetic_order': solved_model.ap_reaction_ord_i
                }
 

            if trajectory_reward > current_best:
                current_best = trajectory_reward
                best_model = (output_model_filename, trajectory_reward, solved_model, Q, model_state)

        if modus == "hierarchic_data":
            return best_model, results_dict
        
        else:
            return best_model[0], best_model[1], best_model[2], best_model[3], best_model[4]

# This is the function for starting with the hydrodynamic model and integrating the reaction data
## This could be easily automized, but I used it manually to get reproducable results (otherwise the topology would change every time)
def run_from_init_topo():
    modus = "hierarchic_data"
    case_study = "tcr-rtd"

    results_path = "./workflow/outputs/results/"
    results_filename = "QUANT_EPS8_2024-07-31_18-13-41"

    results_file = open(results_path + results_filename, 'rb')    
    results_dict = pickle.load(results_file)
    results_file.close()

    e = 9
    topology = results_dict[0][0][e]["best_topology"]

    for compartment in topology.compartments:
        compartment.state = []
    for interface in topology.interfaces:
        interface.state = []
        
    phenomena_module = PhenomenaModule()
    phenomena = phenomena_module.get_phenomena(case_study, modus)

    assembler = AssemblerModule(topology, phenomena)
    assembler.clean_topology()
    abortion_check = assembler.assign_phenomena(modus)

    assembler.generate_state(modus)
    assembler.trace_volume(modus)

    assembler.generate_eqlib(modus)

    input_module = InputModule()
    input_profile = input_module.generate_input_profile(case_study, modus)
    assembler.generate_knownvals(input_profile, modus)
    
    initial_state = assembler.state
    eq_library = assembler.eq_library
    exclusive_eqs = assembler.exclusive_eqs
    known_values = assembler.known_values

    equation_generator = EquationGenerator()

    e_equation_gen = 15
    LL_eps = 0.2

    # topology.print_to_jaal()

    Q_eq_learned = 0 
    current_trajectory = None
    best_model, results_dict = equation_generator.run_workflow(initial_state, 
                                                                known_values, 
                                                                eq_library,
                                                                exclusive_eqs,
                                                                e_equation_gen,
                                                                LL_eps,
                                                                assembler.topology,
                                                                Q_eq_learned,
                                                                current_trajectory,
                                                                modus
                                                                )


    print()