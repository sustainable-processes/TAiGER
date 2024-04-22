import numpy as np
import pandas as pd

from classes_state_representation import DAENode, UnaryOperator, BinaryOperator, NumTerminalNode, SymbTerminalNode, BoundaryCondNode


class EquationGeneratorModule():
    
    """ Class for equation generator module

    For each episode in the workflow, i.e., each trajectory, an
    EquationGeneratorModule (with the name "env") is created.
    Most importantly, this object has the attribute "state" which
    stores the system of equations, i.e., a sequence (list) of unary
    operator, binary operator, numerical value and symbolic
    variable objects. Upon initialization, the symbolic variable
    objects all have the "status" "undecided". One after the other,
    actions are taken on the symbolic nodes. Moreover, the length of 
    the state might change when constitutive equations are added.

    Moreover, the EquationGeneratorModule object has the methods needed
    to change the state.

    Attributes:
        state (list):
            Holds list of node objects that represent the system of equations,
            i.e., the model, in postfix notation.

        input_profile (dict):
            Holds the input profile (a python dictionary).

        eq_library (dict):
            Holds the constitutive equation library (currently a python dict).

        current_trajectory (list):
            Holds a list of tupels where each tuple represents a state-action
            pair on the current trajectory. It is important to keep track of
            the trajectory to correctly distribute the rewards to all state-
            action pairs of the trajectory.

    Methods:
        get_current_undecided_symbolic_node:
            Returns the identifier, i.e., the "unique_representation" attribute
            of the first undecided symbolic node in the state. On this node the
            next action is taken.

        get_actions:
            Returns a list of available actions for the current undecided node.
            Each action in the returned list is a dictionary, where the first
            key "action_type" has a value "substitute_constit", "take_input",
            "make_param", or "neglect". For the former two, it must also be
            specified which constitutive equation is chosen from the library
            or which value is taken from the inputput profile. This is done
            via the second key of the dictionary which is either "library_key"
            or "input_profile_key".

        get_actions_reduced_space:
            If the workflow_modus is "modus-reduced-model-space", 
            "modus-explore-reduced-model-space", or
            "modus-reduced-model-space-learning-curves", not all actions are
            allowed at each state. This is done to ensure that executable models
            as long as a rigorous test module is not implemented. The reduction
            of the action space is implemented through the file
            "reduced_search_space_trajectories" that explicitly contains all
            permissible state-action trajectories. This method returns all
            permissible actions in the reduced search space setting. For that,
            at a given state, the current, uncompleted state-action trajectory
            is compared to all permissible state-action trajectories. All 
            permissible trajectories that start with the same trajectory as
            the current one are identified. Their next actions are compiles
            into a list and returned by this function. The format of the
            returned list is the same as in "get_actions".

        choose_action:
            From the list of actions created by either "get_actions" or
            "get_actions_reduced_space", one action is chosen according
            to the desired training policy. The chosen action is returned
            in the dictionary format described for "get_actions", e.g.,
            [{"action_taken": "substitute_constit", "library_key": "lib_1"}].

        step:
            Modifies the state (state attribute of the EquationGeneratorModule)
            based on the chosen action. Specifically, this corresponds to
            setting the "status" of the currently undecided symbolic node from
            "undecided" to "var_constitutiveequation", "par_inputprofile",
            "make_param", "neglect". For "var_constitutiveequation", the 
            chosen constitutive equation is concatenated to the state. Another
            example: When the parser later iterates through the fully
            specified state, a node with the status "neglect" would be
            translated into a parameter with the value zero.

    """
    
    def __init__(self, initial_state: list, input_profile: dict, eq_library: dict):
        self.state = initial_state
        self.input_profile = input_profile
        self.eq_library = eq_library
        self.current_trajectory = []  # Keeps track of current trajectory (of state-action pairs) to distribute rewards to the visited state-action pairs. Also used to ensure that constitutive equations are only plugged in once. Note that does not record terminal state.

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

    def get_actions(self) -> list:

        """ Returns available actions at given state.
        
        For more details see class docstring.
        """    
         
        available_action_list = [] # List of dictionaries, with "action_type" (always) and "key" (for "action_type": "substitute_constit" and "action_type": "take_input")
        
        # Iterate through state until first undecided symbolic terminal node is found. For this node find actions.
        for node in self.state:  
            if isinstance(node, SymbTerminalNode) and node.status == "undecided":

                # LIBRARY: Check, which equations in the library contain the variable (i.e., the current node): For that, test each equation by iterating all objects and comparing the nodes' unique_representation.
                for key, lib_equation in self.eq_library.items():
                    # If constitutive equation has already been used in the current trajectory, skip to next library item.
                    if any("library_key" in d and d["library_key"] == key for _,d in self.current_trajectory):
                        continue
                    # Check if at least one object in the library equation has the same unique_representation as the node at hand. Makes it a candidate action.
                    if any(node.unique_representation == lib_node.unique_representation or node.der_var == lib_node.unique_representation for lib_node in lib_equation): # Second condition is to ensure that for a node d_j_i_dz a constitutive equation with j_i can also be chosen.
                        available_action_list.append({"action_type": "substitute_constit", "library_key": key})

                # INPUT PROFILE: Check if one or multiple values are provided in the input profile
                if node.unique_representation in self.input_profile:
                    available_action_list.append({"action_type": "take_input", "input_profile_key": node.unique_representation})
                # For now assumes that max one value per variable is provided in the input profile
                # Pseudocode to allow choosing out of multiple candidate values in input_profile. (Assume following naming convention: unique_representation = 'ord_ip' and in input profile as 'ord_ip_1', 'ord_ip_2' (this is their node.inputprofile_representation and their input_profile_key)):
                # if node.unique_representation in """self.input_profile names ohne _2 am Ende"""
                #   # Append one dict for each candidate
                #   available_action_list.append({"action_type": "take_input", "input_profile_key": """representation of FIRST candidate in input profile"""})
                #   available_action_list.append({"action_type": "take_input", "input_profile_key": """representation of SECOND candidate in input profile"""})

                # MAKE PARAMETER FOR ESTIMATION (is a valid action for any symbolic node)
                available_action_list.append({"action_type": "make_param"})

                # NEGLECT (is a valid action for any symbolic node)
                available_action_list.append({"action_type": "neglect"})

                # KEEP DERIVATIVE VARIABLES (such as d_c_i_dz, all four actions above can be performed on der variables as well. In addition, they can just remain as they are. Not all models will be solvable, but solver will tell/teach us.)
                if node.der_var != None:
                    available_action_list.append({"action_type": "keep_derivative"}) # Derivatives are treated as variables in pyomo.

                break
        
        return available_action_list

    def get_actions_reduced_space(self, reduced_search_space_trajectories: dict, action_trajectory: list) -> list:
        
        """ Returns available actions at given state for reduced space operation.
        
        Returns next action, i.e., available actions, from those feasible trajectories that contain the current trajectory at their beginning.
        For more details see class docstring.
        """  
        
        results = []
        for sublist in reduced_search_space_trajectories.values(): # for each stored, feasible trajectory
            if len(sublist) < len(action_trajectory):
                continue  # Skip lists that are shorter than action_trajectory
            
            match = True
            for i in range(len(action_trajectory)):
                if sublist[i] != action_trajectory[i]:
                    match = False
                    break

            if match and len(sublist) > len(action_trajectory): # check that there are still elements left
                results.append(sublist[len(action_trajectory)])

        # Remove duplicates
        seen = set()
        unique_list = []
        for d in results:
            # Convert each dictionary to a frozenset to make it hashable
            frozen_dict = frozenset(d.items())

            if frozen_dict not in seen:
                seen.add(frozen_dict)
                unique_list.append(d)
        
        return unique_list


    def choose_action(self, training_policy: str, epsilon: float, max_epsilon: float, episode: int, available_actions: list, Q: pd.DataFrame) -> dict:

        """ Chooses and returns one action.
        
        For more details see class docstring.
        """    
        
        # TRAINING POLICY 1: eps-greedy-static
        if training_policy == "eps-greedy-static":
            # Example implementation of epsilon greedy: https://www.geeksforgeeks.org/epsilon-greedy-algorithm-in-reinforcement-learning/
            p = np.random.random()
            if p < epsilon: # With probability of epsilon, pick random action from available actions for current state.
                chosen_action = available_actions[np.random.choice(len(available_actions))]
            else: # With probability of 1-epsilon, pick action with largest Q(s,a) value for current state.
                Q_filtered = Q[Q["state"].apply(lambda x: x == self.state)] # only contains actions previously made in the same state
                index_of_Qmax = Q_filtered["Q(s,a)"].idxmax() # ToDo: If mulitple s-a-pairs have same Q value, the first pair is returned. Make it random or do non-zero initialization. For low epsilon this leads to high number of correct identification in first few steps since order of action is constit/input/param/neglect and our target model relies on many constit. Observed trends are still valid.
                chosen_action = Q_filtered.at[index_of_Qmax, "action"]
        
        # TRAINING POLICY 2: eps-greedy-dynamic, epsilon is reduced with every episode
        if training_policy == "eps-greedy-dynamic":
            epsilon = max_epsilon - e * max_epsilon/episodes
            p = np.random.random()
            if p < epsilon: # With probability of epsilon, pick random action from available actions for current state.
                chosen_action = available_actions[np.random.choice(len(available_actions))]
            else: # With probability of 1-epsilon, pick action with largest Q(s,a) value for current state.
                Q_filtered = Q[Q["state"].apply(lambda x: x == self.state)] # only contains actions of current state
                index_of_Qmax = Q_filtered["Q(s,a)"].idxmax() # ToDo: if mulitple s-a-pairs have same Q value, the first pair is returned. Make it random or do non-zero initialization. For low epsilon this leads to high number of correct identification in first few steps since order of action is constit/input/param/neglect and our target model relies on many constit. Observed trends are still valid.
                chosen_action = Q_filtered.at[index_of_Qmax, "action"]

        # TRAINING POLICY 3: Upper Confidence Bound Algorithm (from Browne, 2012)
        if training_policy == "trainingpolicy-3":
            pass
            #M = 1e9
            #Q_filtered = Q[Q["state"].apply(lambda x: x == self.state)] # only contains actions of current state
            #Q_filtered['UCB'] = Q_filtered["Q(s,a)"] + np.where(Q_filtered["noofvisits"] != 0, 2 * (2**(-1/2)) * (2*np.log(Q_filtered["noofvisits"].sum())/Q_filtered["noofvisits"])**(1/2) , M)
            #index_of_Qmax = Q_filtered["UCB"].idxmax() # CAVE, ToDo: if mulitple s-a-pairs have same UCB value, the first pair is returned. Make it random or do non-zero initialization.
            #chosen_action = Q_filtered.at[index_of_Qmax, "action"]
        
        # TRAINING POLICY 4:     
        if training_policy == "trainingpolicy-3":
            pass
            #a = np.argmax(Q[s,:] + np.random.randn(1,self.action_space.n)*(1./(i+1)))

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
                    node.status = "var_constitutiveequation"
                    self.state = self.state + self.eq_library[chosen_action["library_key"]] # Concatenate object-oriented postfix notation of constitutive equation to current DAE. In the added equation some nodes may be "undecided", however since object-oriented programming the variables that have been plugged in already have status var_constitutiveequation and variables that have been choosen for parameter estimation already have the status par_estimation, etc. Thus, constitutive equations are not plugged in multiple times, parameters are estimated always or never, params are always taken from the input profile and neglected consistently. CAVE: If the action "const eq" is chosen for variables introduced to the state through a constitutive equation, they might choose their own const eq to specify them. Prevented by only allowing to pick const equations that do not appear in the trajectory yet (implemented in get_actions()). 
                if chosen_action["action_type"] == "take_input":
                    node.status = "par_inputprofile" # The parser, seeing this status, makes the node a parameter and loads the value from the input profile.
                    node.inputprofile_representation = chosen_action["input_profile_key"] # To allow choosing out of multiple candidate values in input_profile.
                if chosen_action["action_type"] == "make_param":
                    node.status = "par_estimation" # The parser, seeing this status, makes the node a mutable parameter.
                if chosen_action["action_type"] == "neglect":
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