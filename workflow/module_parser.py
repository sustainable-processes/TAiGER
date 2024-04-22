from typing import Tuple

from classes_state_representation import DAENode, UnaryOperator, BinaryOperator, NumTerminalNode, SymbTerminalNode, BoundaryCondNode


class ParserModule():

    def parse_model_to_file(self, state: list, input_profile: dict, output_model_filepath: str) -> Tuple[str, list]:

        """ Create pyomo model from state

        Creates a python file (output_model_filepath) with a function "create_pyomo_model" that 
        contains and returns the pyomo model specified in the state passed to "parse_model_to_file". 
        For that, uses the pyomo_model_template.py file and populates it. 

        Parameters:
            state (list):
                Model that shall be parsed, represented as sequence of operator and node objects.
            input_profile (dict):
                Contains known properties of system, including parameters, initial guesses for
                variables and the dimensions (and bounds) for modeling.
            output_model_filepath (str):
                Filepath where to create python file with function that returns pyomo model.
        
        Returns:
            output_model_filepath (str):
                Filepath where to create python file with function that returns pyomo model.
            theta_names (list):
                List of names of the model parameters that shall be fitted in the solver and 
                parameter estimation module.
        """

        # PARSE STATE TO PYOMO MODEL FORMULATION
        tokenStack = []
        equation_counter = 1
        theta_names = [] # Records parameters that shall be estimated

        lines_block_1 = [] # Stores lines to insert into block 1 in template file
        lines_block_2 = [] # Stores lines to insert into block 2 in template file
        lines_block_3a = [] # Stores lines to insert into block 3 in template file # Distinction in 3a for Var and 3b for DerivativeVariable, since the former need to be instantiated first.
        lines_block_3b = [] # Stores lines to insert into block 3 in template file
        lines_block_4 = [] # Stores lines to insert into block 4 in template file

        # Before we start parsing the model we have to check for some logical challenges:
        # CHALLENGE: When declaring a derivative variable, the basis variable must exist in pyomo (but does not need to be in any of the equations).
            # Action 1: put basis var in variable block so that it exists, even if not a later state.
            # Action 2: if basis var occurs in state at later point, make it "var_constitutive" (unless it already is desired_var). Will not be in lines_block twice, ensured by list(set(list)).
            # Action 3: scan the state up to this point and check if basis var has already occured. If yes, change status to "var_constitutive".
        for node in state:
            #if isinstance(node, SymbTerminalNode) and (node.der_var == ["c_i"] or node.der_var == ["j_i"]): # for all derivative variables (Leave out v_z and accept logical error/resulting failure. Reason: v_z would be with status "var_constitutiveequation" but doesnt have an index, causes problems in "#Populate Block 3".)
            if isinstance(node, SymbTerminalNode) and node.der_var != None and (node.status == "var_constitutiveequation" or node.status == "var_keepderivative"): # for all derivative variables that are meant to go into the variable section.
                for node2 in state: # check each nodes if they are the derivative's basis variable. If they occur, the next line ensures that they are variables.
                    if node2.unique_representation == node.der_var[0] and node2.status != "var_desired" and node2.status != "var_constitutiveequation": # need to turn basis variable into variable if not already a variable.
                        node2.status = "var_constitutiveequation" # Ggf this means a change away from "par_inputprofile", "neglect", par_estimation
                # now the derivative's base variable is a variable - given the base var is somewhere in the state.
                # To ensure that the base variable is in lines_block_3a (even when the base variable does not occur in the state) write it to lines_block_3a. Cave Todo: this part is not generic, does not allow extension to other var/derivative variables without including them here.
                if node.der_var == ["j_i"]:
                    lines_block_3a.append("   m.j_i = Var(m.z, m.i)\n") # duplicates are deleted further down with "set(list)"
                elif node.der_var == ["c_i"]:
                    lines_block_3a.append("   m.c_i = Var(m.z, m.i)\n")
                # See above why we exclude v_z
                elif node.der_var == ["v_z"]:
                    lines_block_3a.append("   m.v_z = Var()\n")

        inputTokens = state
        for node in inputTokens:
            
            operand1 = None
            operand2 = None
            result = None

            if isinstance(node, UnaryOperator): # No need to introduce parentheses, since included in pyomo string anyway.
                operand1 = tokenStack.pop()
                # The following three are the only instances of UnaryOperators in my example. Find different solution later to generalize code.
                if node.unique_representation == "sumop_p":
                    result = node.pyomo_representation + operand1 + " for p in range(1,1+input_profile['sets']['p']['max']))"
                elif node.unique_representation == "prodop_i":
                    result = node.pyomo_representation + operand1 + " for i in range(1,1+input_profile['sets']['i']['max']))"
                elif node.unique_representation == "expon":
                    result = node.pyomo_representation + operand1 + ")"
                tokenStack.append(result)
            elif isinstance(node, BinaryOperator): # Parentheses are required for binary operator (would not if we evaluate, thanks to postfix, but we print the expression).
                operand2 = tokenStack.pop()
                operand1 = tokenStack.pop()
                #result = "(" + operand1 + node.pyomo_representation + operand2 + ")" # parentheses necessary?
                result = "(" + operand1 + " " + node.pyomo_representation + " " + operand2 + ")" 
                tokenStack.append(result)
            else:
                tokenStack.append(node.pyomo_representation)

            # Populate block 1 (sets). Collect all indices that are used and add them to block 1, which is where sets are defined in pyomo. For that look up in the input profile, whether index is continuous or discrete. Therefore, only works for indices that are also defined in the input profile.
            _indexlist = []
            if isinstance(node, UnaryOperator) and node.op_indices != None:
                _indexlist = node.op_indices
            elif isinstance(node, BinaryOperator) and node.eq_indices != None:
                _indexlist = node.eq_indices
            elif isinstance(node, SymbTerminalNode) and node.var_indices != None:
                _indexlist = node.var_indices
            if _indexlist != []:
                for index in _indexlist:
                    if input_profile['sets'][index]['type'] == "continuous":
                        lines_block_1.append(f"   m.{index} = ContinuousSet(bounds=({input_profile['sets'][index]['min']},{input_profile['sets'][index]['max']}), initialize=m.zOfMeas)\n") # CAVE: when more continuous variables than z are added, "initialize=m.measZ" must be done more generic.
                    elif input_profile['sets'][index]['type'] == "discrete":
                        lines_block_1.append(f"   m.{index} = RangeSet({input_profile['sets'][index]['min']},{input_profile['sets'][index]['max']})\n")
            lines_block_1 = list(set(lines_block_1)) # delete duplicates that would occur when an index occurs multiple times

            # Populate block 2 (parameters).
            if isinstance(node, SymbTerminalNode):
                if node.status == "par_inputprofile":
                    if node.var_indices == None: # depending on whether the parameter has indices the pyomo code has to consider the indexes or not
                        #lines_block_2.append(f"   m.{node.unique_representation} = Param(initialize={input_profile[node.unique_representation]})\n") # Assumes that only one value for each variable is given in the input profile
                        lines_block_2.append(f"   m.{node.unique_representation} = Param(initialize={input_profile[node.inputprofile_representation]})\n") # To allow choosing out of multiple candidate values in input_profile.
                    else:
                        _indices = ", ".join([f"m.{_index}" for _index in node.var_indices])
                        #lines_block_2.append(f"   m.{node.unique_representation} = Param({_indices}, initialize={input_profile[node.unique_representation]})\n") # Assumes that only one value for each variable is given in the input profile
                        lines_block_2.append(f"   m.{node.unique_representation} = Param({_indices}, initialize={input_profile[node.inputprofile_representation]})\n") # To allow choosing out of multiple candidate values in input_profile.
                elif node.status == "par_estimation":
                    theta_names.append(node.unique_representation)
                    if node.var_indices == None:
                        # For estimating parameters in parmest, they can either be provided as "mutable parameters":
                        lines_block_2.append(f"   m.{node.unique_representation} = Param(initialize=input_profile[\"{node.unique_representation}\"], mutable=True) # This parameter is to be estimated.\n")
                        # ... or as "variables". The latter allows the specification of bounds.
                        ### lines_block_2.append(f"   m.{node.unique_representation} = Var(initialize=input_profile[\"{node.unique_representation}\"]) # This parameter is to be estimated.\n")    
                        # However, I decided to not provide any initialization for parameter estimation (to avoid the error that occurs when a node is chosen for estimation although no starting value is provided. Moreover, values in the problem profile are meant to be "known" values - for initial guesses find other solution.)
                        ### lines_block_2.append(f"   m.{node.unique_representation} = Var() # This parameter is to be estimated.\n")
                    else:
                        _indices = ", ".join([f"m.{_index}" for _index in node.var_indices])
                        lines_block_2.append(f"   m.{node.unique_representation} = Param({_indices}, initialize=input_profile[\"{node.unique_representation}\"], mutable=True) # This parameter is to be estimated.\n")
                        ### lines_block_2.append(f"   m.{node.unique_representation} = Var({_indices}, initialize=input_profile[\"{node.unique_representation}\"]) # This parameter is to be estimated.\n")
                        ### lines_block_2.append(f"   m.{node.unique_representation} = Var({_indices}) # This parameter is to be estimated.\n")
                elif node.status == "neglected":
                    if node.var_indices == None:
                        lines_block_2.append(f"   m.{node.unique_representation} = Param(initialize=0)\n") # Neglected terms/nodes are treated as parameters with value 0. Also works for multidimensional params: all values are set to zero.    
                    else:
                        _indices = ", ".join([f"m.{_index}" for _index in node.var_indices])
                        lines_block_2.append(f"   m.{node.unique_representation} = Param({_indices}, initialize=0)\n") # Neglected terms/nodes are treated as parameters with value 0.  Also works for multidimensional params: all values are set to zero.
                lines_block_2 = list(set(lines_block_2)) # delete duplicates that would occur when a parameter occurs multiple times
                
            # Populate block 3 (variables).
            if isinstance(node,SymbTerminalNode):
                if (node.status == "var_constitutiveequation" or node.status == "var_desired") and node.der_var == None: # is not a derivative variable
                    if node.var_indices == None:
                        lines_block_3a.append(f"   m.{node.unique_representation} = Var()\n")
                    else:
                        _indices = ", ".join([f"m.{_index}" for _index in node.var_indices])
                        lines_block_3a.append(f"   m.{node.unique_representation} = Var({_indices})\n")
                elif (node.status == "var_constitutiveequation" or node.status == "var_desired" or node.status == "var_keepderivative") and node.der_var != None: # is a derivative variable
                    _indices1 = ", ".join([f"m.{_index}" for _index in node.der_var])
                    _indices2 = ", ".join([f"m.{_index}" for _index in node.der_wrt])
                    lines_block_3b.append(f"   m.{node.unique_representation} = DerivativeVar({_indices1}, wrt={_indices2})\n")            
                lines_block_3a = list(set(lines_block_3a)) # delete duplicates that would occur when a variable occurs multiple times
                lines_block_3b = list(set(lines_block_3b)) # delete duplicates that would occur when a variable occurs multiple times
                # Handling derivative variables is tricky BECAUSE: are handled as variables in pyomo but as operators in our logic. -- This is not true, though.

            # Populate block 4 (equations). If node is "==" that means in postfix notation, that an equation is entirely expressed and can be pushed to lines_block_5. The tokenStack is cleared for the next equation.
            if node.pyomo_representation == "==":
                # The equal object stores, how many dimensions the equation has, e.g., one equation for each z and i. 
                _indices1 = ", ".join(node.eq_indices)
                _indices2 = ", ".join([f"m.{_index}" for _index in node.eq_indices])
                lines_block_4.append(f"   def _eq{equation_counter}_rule(m, {_indices1}):\n      return {tokenStack[0]}\n   m.eq{equation_counter} = Constraint({_indices2}, rule=_eq{equation_counter}_rule)\n\n")
                equation_counter += 1
                tokenStack = []

        # PRINT PYOMO FORMULATION INTO PYOMO TEMPLATE FILE
        template_file_path = './workflow/pyomo_model_template.py'
        
        # Open the template file for reading
        with open(template_file_path, 'r') as file:
            template_content = file.readlines()

        # Add lines. Find the correct position in the template by searching for the "End: Block ..."-cue phrase.
        for blocknumber in range(1,5):
            position = template_content.index(f"   # End: Block {blocknumber}\n")
            if blocknumber == 1:
                template_content[position:position] = lines_block_1
            elif blocknumber == 2:
                template_content[position:position] = lines_block_2
            elif blocknumber == 3:
                lines_block_3 = lines_block_3a + lines_block_3b # var and derivativevar are collected separately, since the former must be instantiated first
                template_content[position:position] = lines_block_3
            elif blocknumber == 4:
                template_content[position:position] = lines_block_4
        
        # Write the modified content back to the file
        with open(output_model_filepath, 'w') as file:
            file.writelines(template_content)

        model_filepath = output_model_filepath

        return model_filepath, theta_names


