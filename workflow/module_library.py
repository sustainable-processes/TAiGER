from typing import Tuple

from classes_state_representation import DAENode, UnaryOperator, BinaryOperator, NumTerminalNode, SymbTerminalNode, BoundaryCondNode

class LibraryModule():

    def generate_initial_state_and_lib(self) -> Tuple[list, dict]:

        # DEFFINE ALL NODES NEEDED FOR THE INITIAL STATE OR THE CONSTITUTIVE EQUATIONS
        
        # Define binary operators
        plus = BinaryOperator("+", "+", None)
        minus = BinaryOperator("-", "-", None)
        multi = BinaryOperator("*", "*", None)
        divid = BinaryOperator("/", "/", None)
        #equal_tzi = BinaryOperator("=", "==", ['t','z','i']) # equation index only applies to =
        equal_zi = BinaryOperator("=", "==", ['z','i']) # equation index only applies to =
        equal_zp = BinaryOperator("=", "==", ['z','p']) # equation index only applies to =
        equal_p = BinaryOperator("=", "==", ['p']) # equation index only applies to =
        equal_i = BinaryOperator("=", "==", ['i']) # equation index only applies to =
        power = BinaryOperator("^", "**", None)

        # Define unary operators (Defining new unary operators requires adding pyomo string to the parser itself.)
        expon = UnaryOperator("expon", "exp(", None) # Specify index on which to perform operator, doesnt apply to exp. CAVE: Some additional pyomo string is provided in the parser itself.
        sumop_p = UnaryOperator("sumop_p", "sum(", ['p']) # CAVE: Some additional pyomo string is provided in the parser itself.
        prodop_i = UnaryOperator("prodop_i", "prod(", ['i']) # CAVE: Some additional pyomo string is provided in the parser itself.

        # Define numerical terminal nodes
            # These are determined directly in the constructor.

        # Define symbolic terminal nodes
        c_i = SymbTerminalNode("c_i", "m.c_i[z,i]", ['z','i'], None, None) # pass None if no indices
        c_i.status = "var_desired"
        #d_c_i_dt = SymbTerminalNode("d_c_i_dt", "m.d_c_i_dt[t,i]", ['t','i'], ["c_i"], ['t'])
        #d_c_i_dt = SymbTerminalNode("d_c_i_dt", "m.d_c_i_dt[z,i]", ['z','i'], ["c_i"], ['t'])
        d_c_i_dz = SymbTerminalNode("d_c_i_dz", "m.d_c_i_dz[z,i]", ['z','i'], ["c_i"], ['z'])
        d_j_i_dz = SymbTerminalNode("d_j_i_dz", "m.d_j_i_dz[z,i]", ['z','i'], ["j_i"], ['z'])
        d_v_z_dz = SymbTerminalNode("d_v_z_dz", "m.d_v_z_dz[z,i]", ['z','i'], ["v_z"], ['z'])
        v_z = SymbTerminalNode("v_z", "m.v_z", None, None, None) # Cave: should they have a resolution?! Subscript does not mean resolution in this case. Change in "Challenge 1" in the parser code as well.
        j_i = SymbTerminalNode("j_i", "m.j_i[z,i]", ['z','i'], None, None)
        r_i = SymbTerminalNode("r_i", "m.r_i[z,i]", ['z','i'], None, None)
        r_p = SymbTerminalNode("r_p", "m.r_p[z, p]", ['z', 'p'], None, None)
        nu_ip = SymbTerminalNode("nu_ip", "m.nu_ip[i, p]", ['i','p'], None, None)
        k_p = SymbTerminalNode("k_p", "m.k_p[p]", ['p'], None, None)
        ord_ip = SymbTerminalNode("ord_ip", "m.ord_ip[i,p]", ['i','p'], None, None)
        k_ref_p = SymbTerminalNode("k_ref_p", "m.k_ref_p[p]", ['p'], None, None)
        E_p = SymbTerminalNode("E_p", "m.E_p[p]", ['p'], None, None)
        R = SymbTerminalNode("R", "m.R", None, None, None)
        T_ref = SymbTerminalNode("T_ref", "m.T_ref", None, None, None)
        T = SymbTerminalNode("T", "m.T", None, None, None)
        D_z = SymbTerminalNode("D_z", "m.D_z", None, None, None) # Cave: should they have a resolution?! Subscript does not mean resolution in this case.

        # Define boundary condition nodes:
        BC_c0 = BoundaryCondNode("BC_c0","m.c_i[0,i] - m.c_i0[i]")
        BC_dj_i_dz_L = BoundaryCondNode("BC_dj_i_dz_L", "m.d_j_i_dz[input_profile['sets']['z']['max'],i]")

        # DEFINE INITIAL STATE (general differential mass balance)
        initial_state = [NumTerminalNode('0','0'), v_z, d_c_i_dz, multi, c_i, d_v_z_dz, multi, d_j_i_dz, r_i, minus, plus, plus, equal_zi, NumTerminalNode('0','0'), BC_c0, equal_i]
        #initial_state = [NumTerminalNode('0','0'), d_c_i_dt, v_z, d_c_i_dz, multi, c_i, d_v_z_dz, multi, d_j_i_dz, r_i, minus, plus, plus, plus, equal_tzi, NumTerminalNode('0','0'), BC_c0, equal_i]
        
        # DEFINE LIBRARY OF CONSTITUTIVE EQUATIONS (a small library at the moment)
        eq_library = {
            'lib_1': [NumTerminalNode('0','0'), r_p, nu_ip, multi, sumop_p, r_i, minus, equal_zi],
            'lib_2': [NumTerminalNode('0','0'), k_p, c_i, ord_ip, power, prodop_i, multi, r_p, minus, equal_zp], 
            'lib_3': [NumTerminalNode('0','0'), k_ref_p, E_p, R, divid, NumTerminalNode('1','1'), T_ref, divid, NumTerminalNode('1','1'), T, divid, minus, multi, expon, multi, k_p, minus, equal_p], 
            'lib_4': [NumTerminalNode('0','0'), NumTerminalNode('-1','-1'), D_z, d_c_i_dz, multi, multi, j_i, minus, equal_zi, NumTerminalNode('0','0'), BC_dj_i_dz_L, equal_i]
            }

        return initial_state, eq_library
