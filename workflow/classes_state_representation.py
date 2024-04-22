class DAENode:

    """ Base class for "nodes"

    In this work, systems of equations are represented as sequence of
    "nodes" where the four types of nodes include unary operators,
    binary operators, numerical values, and symbolic variables.

    Attributes:
        unique_representation (str):
            Unique "name" of the node. E.g. "v_z" for the axial
            flow velocity, or "plus" for the addition operator.

        pyomo_representation (str):
            Contains string that is needed to represent this node
            in pyomo syntax. E.g. "m.v_z[z]" for a symbolic
            variable v_z that belongs to model m and is indexed
            over reactor length z. Or "+" for the binary addition
            operator.
    """

    def __init__ (self, unique_representation: str, pyomo_representation: str):
        self.unique_representation = unique_representation
        self.pyomo_representation = pyomo_representation

    def __eq__(self, other): # Makes it possible to check with == if objects of this class (or the inheriting classes) have same value for all attributes
        return self.__dict__ == other.__dict__


class UnaryOperator(DAENode):

    """ Class for unary operators

    The summation operator (large sigma) and the product operator
    (large pi) are the only unary operators that require the 
    specification over which index the summation/multiplication
    is performed. The index(es) are provided in the attribute
    op_indices.

    Attributes:
        op_indices (list or None):
            For summation or product operators specifies index
            over which summation/multiplication takes place.
            Leave free when instantiating a different unary 
            operator. Always pass indices in order 
            ['t', 'x', 'y', 'z', 'i', 'p'].
    """

    def __init__ (self, unique_representation: str, pyomo_representation: str, op_indices: list):
        super().__init__(unique_representation, pyomo_representation)
        self.op_indices = op_indices # Takes the indices as list. Always store indices in the order ['t', 'x', 'y', 'z', 'i', 'p']


class BinaryOperator(DAENode):
    
    """ Class for binary operators

    The equal operator is the only binary operators that requires
    the specification of one or multiple indices. For example, a
    constraint equation may apply for each chemical species i and
    at each position z along the spatial coordinate. To capture
    this information in the sequential state (and not concatenate
    the equation for every single species or position), all such 
    indices are collected in the eq_indices attribute of the 
    equation's equal operator.

    Attributes:
        eq_indices (list or None):
            For equal operators specify dimensions in which this
            constraint holds. Always pass indices in order 
            ['t', 'x', 'y', 'z', 'i', 'p'].
    """
    
    def __init__ (self, unique_representation: str, pyomo_representation: str, eq_indices: list):
        super().__init__(unique_representation, pyomo_representation)
        self.eq_indices = eq_indices # Always store indices in order ['t', 'x', 'y', 'z', 'i', 'p']


class NumTerminalNode(DAENode):

    """ Class for numerical values

    Holds numerical values such as 0, 1, 3.14. Does not require 
    attributes beyond those defined by the parent class.

    """

    pass # The value is determined in constructor


class SymbTerminalNode(DAENode):

    """ Class for symbolic variables

    The workflow specifies the general differential balance
    equation by performing actions on symbolic variables. To
    begin with symbolic variables have the status "undecided".
    Depending on the action that is taken on the variable, its
    status can change to "var_constitutiveequation",
    "par_inputprofile", "par_estimation", "neglected". The
    workflow does not perform actions on the concentration
    (or its derivatives) since this is the desired variable
    in the equation system that we want to solve for.
    Therefore the symbolic node c_iz has the status
    "var_desired" from the beginning.
    
    Attributes:
        status (str):
            Initialized to "undecided". Once a decision has 
            been made, it is recorded in the status with
            "var_constitutiveequation", "par_inputprofile",
            "par_estimation", "neglected". 
            
        var_indices (list or None):
            Stores indices of that variable. E.g., ['z','i']
            for the concentration should there be more than
            one species i and should it depend on the
            spatial coordinate z. Always pass indices in order 
            ['t', 'x', 'y', 'z', 'i', 'p'].
            
        der_var (list or None):
            If the variable is a derivative variable, e.g.,
            d_c_i_d_z, this attribute holds the 
            "unique_representation" of the derived quantity,
            i.e., ["c_i"]. If not a derivative variable, "None".

        der_wrt (list or None):
            If the variable is a derivative variable, e.g.,
            d_c_i_d_z, this attribute holds the index with respect
            to which the derivative is formed, i.e., ["i"]. If not 
            a derivative variable, "None".

        inputprofile_representation (str):
            When the action "choose value from input profile" is
            taken for a variable, this attribute records the name
            of the variable in the input profile (especially
            important if multiple values for the same variable
            exist in the problem profile). For other actions this
            attribute remains with its initialized value: None.

    """

    def __init__ (self, unique_representation: str, pyomo_representation: str, var_indices: list, der_var: list, der_wrt: list):
        super().__init__(unique_representation, pyomo_representation)
        self.status = "undecided" # Symbolic terminal nodes have status. Other valid statusses are var_desired, var_constitutiveequation, par_inputprofile, par_estimation, neglected.
        self.var_indices = var_indices # Always pass indices in order ['t', 'x', 'y', 'z', 'i', 'p'].
        self.der_var = der_var # At several opportunities, it is checked if this field is "None" (node is not derivative variable) or not (node is derivative variable)
        self.der_wrt = der_wrt # If node is derivative variable, der_wrt records "with respect to" which continuous variable.
        self.inputprofile_representation = None # To allow choosing out of multiple candidate values in input_profile. Is set in Environment.step() to decide for nodes dedicated to be filled with a value from input_profile, which one is used (for all nodes throughout the state!).


class BoundaryCondNode(DAENode): 

    """ Class for initial and boundary conditions

    In the current implementation, at the end of each equation in the 
    library that requires a new IC or BC, such a condition is provided 
    as equation, readily prepared in pyomo string code (see 
    module_library.py). However, knowing when to add which BC requires 
    a priori understanding of the system and should therefore be 
    optimized in future implementations. 
    """
    pass    # value is determined in constructor
