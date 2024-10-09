import numpy as np
import pandas as pd
from typing import Tuple
import copy
from classes_state_representation import DAENode, UnaryOperator, BinaryOperator, NumTerminalNode, SymbTerminalNode, BoundaryCondNode


class EquationGeneratorModule():
        
    def __init__(self, initial_state: list, input_profile: dict, eq_library: dict, exclusive_eqs: list, topology):
        self.state = initial_state
        self.input_profile = input_profile
        self.eq_library = eq_library
        self.exclusive_eqs = exclusive_eqs
        self.current_trajectory = []  # Keeps track of current trajectory (of state-action pairs) to distribute rewards to the visited state-action pairs. Also used to ensure that constitutive equations are only plugged in once. Note that does not record terminal state.
        self.topology = topology # DEBUG

    def get_current_undecided_symbolic_node(self) -> str:

        """Return unique representation of next undecided symbolic node
        
        For more details see class docstring.
        """
        current_undecided_symbolic_node = None

        # Iterate through state until first undecided symbolic node is found.
        for node in self.state:  
            if isinstance(node, SymbTerminalNode) and node.status == "undecided":
                current_undecided_symbolic_node = node.unique_representation
                return current_undecided_symbolic_node
            
        # return current_undecided_symbolic_node

    def assign_measurement_quantities(self, modus):
        for node in self.state:

            if modus == "normal" or modus == "hierarchic_data":
                for var in self.input_profile["measured_var"]:
                    if node.unique_representation in var:
                        node.status = "var_measured"
            
                for var in self.input_profile["manipulated_var"]:
                    if node.unique_representation in var:
                        node.status = "var_manipulated"
            
            if modus == "rtd":
                for var in self.input_profile["measured_var"]:
                    if node.unique_representation in var:
                        node.status = "var_measured_varying_input"

                for var in self.input_profile["manipulated_var"]:
                    if node.unique_representation in var:
                        node.status = "var_manipulated_varying_input"


    def get_actions_reduced_space(self) -> list:

        """ Returns available actions at given state.
        
        For more details see class docstring.
        """    
         
        available_action_list = [] # List of dictionaries, with "action_type" (always) and "key" (for "action_type": "substitute_constit" and "action_type": "take_input")
        action_list_substitute = []
        action_list_input = []
        action_list_parameter = []
        action_list_derivative = []
        # Iterate through state until first undecided symbolic terminal node is found. For this node find actions.
        for node in self.state: 
                 
            if isinstance(node, SymbTerminalNode) and node.status == "undecided":
                # LIBRARY: Check, which equations in the library contain the variable (i.e., the current node): For that, test each equation by iterating all objects and comparing the nodes' unique_representation.
                for key, lib_equation in self.eq_library.items():
                    # If constitutive equation has already been used in the current trajectory, skip to next library item.
                    if any("library_key" in d and d["library_key"] == key for _,d in self.current_trajectory) or any("library_key" in d and d["library_key"] == key_ex for exclusive_eqs_pair in self.exclusive_eqs for key_ex in exclusive_eqs_pair if key in exclusive_eqs_pair for _,d in self.current_trajectory):
                        continue

                    # Check if at least one object in the library equation has the same unique_representation as the node at hand. Makes it a candidate action.
                    if any(node.unique_representation == lib_node.unique_representation or node.der_var == lib_node.unique_representation for lib_node in lib_equation): # Second condition is to ensure that for a node d_j_i_dz a constitutive equation with j_i can also be chosen.
                        if not node.unique_representation in self.input_profile:
                            action_list_substitute.append({"action_type": "substitute_constit", "library_key": key})

                # INPUT PROFILE: Check if one or multiple values are provided in the input profile
                if node.unique_representation in self.input_profile:
                    action_list_input.append({"action_type": "take_input", "input_profile_key": node.unique_representation})
                else:
                    for i in range(1, 5): # For now, only allow to take input values for four variants. ToDo: Generalize for arbitrary number of input variants.
                        if node.unique_representation + "_A" + str(i) in self.input_profile:
                            action_list_input.append({"action_type": "take_input", "input_profile_key": node.unique_representation + "_A" + str(i)})    

                # MAKE PARAMETER FOR ESTIMATION (is a valid action for any symbolic node)
                if node.special_type == "parameter":
                    # if not node.unique_representation in self.input_profile: # ALWAYS TAKE INPUT VALUE IF AVAILABLE
                    action_list_parameter.append({"action_type": "make_param"})

                # KEEP DERIVATIVE VARIABLES (such as d_c_i_dz, all four actions above can be performed on der variables as well. In addition, they can just remain as they are. Not all models will be solvable, but solver will tell/teach us.)
                if node.der_var != None:
                    action_list_derivative.append({"action_type": "keep_derivative"}) # Derivatives are treated as variables in pyomo.
                
                available_action_list = [action_list_substitute,action_list_input,action_list_parameter,action_list_derivative]

                if all(action_list == [] for action_list in available_action_list):
                    # self.topology.print_to_jaal()
                    print("Index issue.")

                break
        
        return available_action_list

    def choose_action(self, epsilon: float, available_actions: list, Q: pd.DataFrame) -> dict:
        # Example implementation of epsilon greedy: https://www.geeksforgeeks.org/epsilon-greedy-algorithm-in-reinforcement-learning/
        p = np.random.random()
        if p < epsilon: # With probability of epsilon, pick random action from available actions for current state.
            p_basic_decision = np.random.randint(0,4)
            while len(available_actions[p_basic_decision]) == 0:
                p_basic_decision = np.random.randint(0,4)
            chosen_action = available_actions[p_basic_decision][np.random.choice(len(available_actions[p_basic_decision]))]
        else: # With probability of 1-epsilon, pick action with largest Q(s,a) value for current state.
            Q_filtered = Q[Q["state"].apply(lambda x: x == self.state)] # only contains actions previously made in the same state
            if len(Q_filtered) > 0:
                index_of_Qmax = Q_filtered["Q(s,a)"].idxmax() # ToDo: If mulitple s-a-pairs have same Q value, the first pair is returned. Make it random or do non-zero initialization. For low epsilon this leads to high number of correct identification in first few steps since order of action is constit/input/param/neglect and our target model relies on many constit. Observed trends are still valid.
                chosen_action = Q_filtered.at[index_of_Qmax, "action"]
            else:
                p_basic_decision = np.random.randint(0,4)
                while len(available_actions[p_basic_decision]) == 0:
                    p_basic_decision = np.random.randint(0,4)
                chosen_action = available_actions[p_basic_decision][np.random.choice(len(available_actions[p_basic_decision]))]
        return chosen_action


    def step(self, chosen_action: dict) -> None:

        """ Applies the action to the state.

        Executes action and updates the state attribute.
        For more details see class docstring.
        """
        
        # GET NEW STATE
        # Iterate through state until first undecided symbolic terminal node is found. For this node apply chosen action.
        for node in self.state:
            
            if isinstance(node, SymbTerminalNode) and node.status == "undecided":
                if chosen_action["action_type"] == "substitute_constit":
                    if "KL" in node.unique_representation:
                        print("")
                    node.status = "var_constitutiveequation"
                    self.state = self.state + self.eq_library[chosen_action["library_key"]] # Concatenate object-oriented postfix notation of constitutive equation to current DAE. In the added equation some nodes may be "undecided", however since object-oriented programming the variables that have been plugged in already have status var_constitutiveequation and variables that have been choosen for parameter estimation already have the status par_estimation, etc. Thus, constitutive equations are not plugged in multiple times, parameters are estimated always or never, params are always taken from the input profile and neglected consistently. CAVE: If the action "const eq" is chosen for variables introduced to the state through a constitutive equation, they might choose their own const eq to specify them. Prevented by only allowing to pick const equations that do not appear in the trajectory yet (implemented in get_actions()). 
                if chosen_action["action_type"] == "take_input":
                    if node.var_indices == ['n']:
                        node.pyomo_representation = node.pyomo_representation[:-3]
                    elif node.var_indices is not None and 'n' in node.var_indices and len(node.var_indices) == 2:
                        node.pyomo_representation = node.pyomo_representation[:-3] + "]"
                    node.status = "par_inputprofile" # The parser, seeing this status, makes the node a parameter and loads the value from the input profile.
                    node.inputprofile_representation = chosen_action["input_profile_key"] # To allow choosing out of multiple candidate values in input_profile.
                if chosen_action["action_type"] == "make_param":
                    if node.var_indices == ['n']:
                        node.pyomo_representation = node.pyomo_representation[:-3]
                    elif node.var_indices is not None:
                        node.pyomo_representation = node.pyomo_representation[:-3] + "]"
                    node.status = "par_estimation" # The parser, seeing this status, makes the node a mutable parameter.
                if chosen_action["action_type"] == "neglect":
                    if node.var_indices == ['n']:
                        node.pyomo_representation = node.pyomo_representation[:-3]
                    elif node.var_indices is not None:
                        node.pyomo_representation = node.pyomo_representation[:-3] + "]"
                    node.status = "neglected" # The parser, seeing this status, makes the node a parameter with value 0.
                if chosen_action["action_type"] == "keep_derivative":
                    node.status = "var_keepderivative" # The parser, seeing this status, makes the node a (derivative) variable.
                break

        # Check if trajectory has terminated, i.e., no undecided nodes remain.
        trajectory_terminated = True
        for node in self.state: # Iterate through state until first undecided symbolic terminal node is found.
            if isinstance(node, SymbTerminalNode) and node.status == "undecided":    
                trajectory_terminated = False
                break

        return trajectory_terminated, self.state