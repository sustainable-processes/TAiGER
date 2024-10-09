from classes_state_representation import *
from classes_compartment_representation import *

# Case Study 1 (PTC)
class ENV_PTC(Compartment):

    def __init__(self, name):
        super().__init__(name)
        self.type = "ENV"
        self.color = 0

        self.Tc = SymbTerminalNode(self.name + "_Tc","m." + self.name + "_Tc[n]",['n'],None,None,lb=0)
        
        self.connections = [{"connection_type":VALVE, "direction":"in", "id": 3},
                            {"connection_type":VALVE, "direction":"in", "id": 4},
                            {"connection_type":VALVE, "direction":"out", "id": 1},
                            {"connection_type":VALVE, "direction":"out", "id": 2}
                            ]
    
    def generate_state(self, modus):
        self.state = []
        self.Tc.status = "var_constitutiveequation"
        return True

# Case Study 2 (TCR)
class ENV(Compartment):

    def __init__(self, name):
        super().__init__(name)
        self.type = "ENV"
        self.color = 0
        
        self.T = SymbTerminalNode(self.name + "_T","m." + self.name + "_T",None,None,None,lb=0)

        self.connections = [{"connection_type":VALVE, "direction":"in", "id": 2},
                            {"connection_type":VALVE, "direction":"out", "id": 1},
                            ]
    
    def generate_state(self, modus):
        self.T = SymbTerminalNode(self.name + "_T","m." + self.name + "_T",None,None,None,lb=0) # delete, only because result data is old
        self.state = []
        return True
    
class CSTR(Compartment):

    def __init__(self, name):
        super().__init__(name)
        self.type = "CSTR"
        self.color = 1

        self.connections = [{"connection_type":VALVE, "direction":"in", "id": 1},
                            {"connection_type":VALVE, "direction":"out", "id": 2},
                            {"connection_type":FILM, "direction":"in", "id": 3},
                            {"connection_type":FILM, "direction":"out", "id": 4}
                            ]
        
    def generate_state(self, modus):
        
        if modus == "normal":

            self.V = SymbTerminalNode(self.name + "_V","m." + self.name + "_V",None,None,None,lb=1e-6)

            for phenomenon in [phenomenon for phenomenon in self.phenomena if phenomenon.type == "phase"]:
                setattr(self, phenomenon.identifier + "R", SymbTerminalNode(self.name + "_" + phenomenon.identifier + "R","m." + self.name + "_" + phenomenon.identifier + "R[i,p,n]",['i','p','n'],None,None,lb=-1,ub=1))

            self.F_in = next((interface.symbol["massflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), None)
            self.F_out = next((interface.symbol["massflow"] for interface in self.interfaces_out if interface.connection_from_id == 2), None)

            if next((interface.symbol["massflow"] for interface in self.interfaces_in if interface.connection_to_id == 3), None) is not None:
                self.J = [next((interface.symbol["massflow"] for interface in self.interfaces_in if interface.connection_to_id == 3))]
                self.A = next((interface.symbol["surface"] for interface in self.interfaces_in if interface.connection_to_id == 3))
                self.Pv = next((interface.symbol["energyflow"] for interface in self.interfaces_in if interface.connection_to_id == 3))
            if next((interface.symbol["massflow"] for interface in self.interfaces_out if interface.connection_from_id == 4), None) is not None:
                self.J = [NumTerminalNode('0','0'),next((interface.symbol["massflow"] for interface in self.interfaces_out if interface.connection_from_id == 4)),self.math.minus]
                self.A = next((interface.symbol["surface"] for interface in self.interfaces_out if interface.connection_from_id == 4))
                self.Pv = next((interface.symbol["energyflow"] for interface in self.interfaces_out if interface.connection_from_id == 4)) 

            self.V_dot = next((interface.symbol["volumeflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), None)
            self.V_dot_out = next((interface.symbol["volumeflow"] for interface in self.interfaces_out if interface.connection_from_id == 2), None)

            self.state = [NumTerminalNode('0','0'),self.F_in,self.F_out,self.math.minus]
            for phenomenon in [phenomenon for phenomenon in self.phenomena if phenomenon.type == "phase"]:
                self.state.append(self.V)
                self.state.append(getattr(self, phenomenon.identifier + "R"))
                self.state.append(self.math.multi)
            if any([type(interface) == FILM for interface in self.interfaces_in + self.interfaces_out]):
                self.state.append(self.A)
                self.state.extend(self.J)
                self.state.append(self.math.multi)
            for phenomenon in [phenomenon for phenomenon in self.phenomena if phenomenon.type == "phase"]:
                self.state.append(self.math.plus)
            if any([type(interface) == FILM for interface in self.interfaces_in + self.interfaces_out]):
                self.state.append(self.math.plus)
            self.state.append(self.math.equal_ip)

            self.state.extend([self.V_dot,self.V_dot_out,self.math.equal])
            
            self.F_out.status = "var_constitutiveequation"
            self.V_dot_out.status = "var_constitutiveequation"

        if modus == "rtd":

            self.V = SymbTerminalNode(self.name + "_V","m." + self.name + "_V",None,None,None,special_type="parameter",lb=1e-6,ub=20)

            self.c_in = next((interface.symbol["massflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), None)
            self.c_out = next((interface.symbol["massflow"] for interface in self.interfaces_out if interface.connection_from_id == 2), None)

            self.dcdt = SymbTerminalNode(self.name + "_dcdt", "m." + self.name + "_dcdt[t]", ['t'], [self.c_out.unique_representation], ['t'])
            
            self.V_dot = next((interface.symbol["volumeflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), None)
            self.V_dot_out = next((interface.symbol["volumeflow"] for interface in self.interfaces_out if interface.connection_from_id == 2), None)

            self.state = [self.V,self.dcdt,self.math.multi,self.c_in,self.c_out,self.math.minus,self.V_dot,self.math.multi,self.math.equal_texept0]

            self.state.extend([self.V_dot,self.V_dot_out,self.math.equal_noind])

            if not self.interfaces_in[0].is_envflow_out:
                self.state.extend([self.c_out,self.math.index0,NumTerminalNode('0','0'),self.math.equal_noind])
            else:
                self.state.extend([self.c_out,self.math.index0,self.c_in,self.math.index0,self.V,self.math.divid,self.math.equal_noind])

            
            self.c_out.status = "var_constitutiveequation"
            self.V_dot_out.status = "var_constitutiveequation"

        if modus == "hierarchic_data":

            self.V = SymbTerminalNode(self.name + "_V","m." + self.name + "_V",None,None,None,lb=1e-6)

            for phenomenon in [phenomenon for phenomenon in self.phenomena if phenomenon.type == "reaction"]:
                setattr(self, phenomenon.identifier + "R", SymbTerminalNode(self.name + "_" + phenomenon.identifier + "R","m." + self.name + "_" + phenomenon.identifier + "R[i]",['i'],None,None,lb=-10,ub=10))

            self.c_in = next((interface.symbol["massflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), None)
            self.c_out = next((interface.symbol["massflow"] for interface in self.interfaces_out if interface.connection_from_id == 2), None)

            self.V_dot = next((interface.symbol["volumeflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), None)
            self.V_dot_out = next((interface.symbol["volumeflow"] for interface in self.interfaces_out if interface.connection_from_id == 2), None)

            self.state = [NumTerminalNode('0','0'),self.c_in,self.c_out,self.math.minus,self.V_dot,self.math.multi]

            self.math.equal_isolo = BinaryOperator("=", "==", ['i']) # equation index only applies to =

            for phenomenon in [phenomenon for phenomenon in self.phenomena if phenomenon.type == "reaction"]:
                self.state.append(self.V)
                self.state.append(getattr(self, phenomenon.identifier + "R"))
                self.state.append(self.math.multi)
                self.state.append(self.math.plus)
            self.state.append(self.math.equal_isolo)

            self.state.extend([self.V_dot,self.V_dot_out,self.math.equal_noind])

            self.c_out.status = "var_constitutiveequation"
            self.V_dot_out.status = "var_constitutiveequation"

        return True

class PFR(Compartment):

    def __init__(self, name):
        super().__init__(name)
        self.type = "PFR"
        self.color = 5

        self.connections = [{"connection_type":VALVE, "direction":"in", "id": 1},
                            {"connection_type":VALVE, "direction":"out", "id": 2},
                            ]
        
    def generate_state(self, modus):
        
        if modus == "rtd":
            
            self.V = SymbTerminalNode(self.name + "_V","m." + self.name + "_V",None,None,None,special_type="parameter",lb=1e-6,ub=20)

            self.c_in = next((interface.symbol["massflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), None)
            self.c_out = next((interface.symbol["massflow"] for interface in self.interfaces_out if interface.connection_from_id == 2), None)
            
            self.V_dot = next((interface.symbol["volumeflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), None)
            self.V_dot_out = next((interface.symbol["volumeflow"] for interface in self.interfaces_out if interface.connection_from_id == 2), None)

            self.xtau = SymbTerminalNode(self.name + "_xtau", "m." + self.name + "_xtau[tau]", ['tau'], None, None, special_type = "binary", lb=0, ub=1)

            self.tau = SymbTerminalNode(self.name + "_tau", "m." + self.name + "_tau", None, None, None, lb=0, ub=20)

            self.state = [self.c_out,self.xtau,self.c_in,self.math.shift,self.math.multi,self.math.sumop_tau_iftgeqtau,self.math.equal_t,
                          self.V, self.tau, self.V_dot, self.math.multi, self.math.equal_noind,
                          NumTerminalNode("1","1"),self.xtau,self.math.sumop_tau,self.math.equal_noind,
                          self.tau,self.xtau,self.math.sumop_multitau,self.math.equal_noind
                        ]   

            self.state.extend([self.V_dot,self.V_dot_out,self.math.equal_noind])
            
            self.c_out.status = "var_constitutiveequation"
            self.V_dot_out.status = "var_constitutiveequation"

            self.xtau.status = "var_constitutiveequation"
            self.tau.status = "var_constitutiveequation"

        if modus == "hierarchic_data":
            
            self.V = SymbTerminalNode(self.name + "_V","m." + self.name + "_V",None,None,None)

            for phenomenon in [phenomenon for phenomenon in self.phenomena if phenomenon.type == "reaction"]:
                setattr(self, phenomenon.identifier + "R", SymbTerminalNode(self.name + "_" + phenomenon.identifier + "R","m." + self.name + "_" + phenomenon.identifier + "R[i]",['i'],None,None,lb=-10,ub=10))

            self.c_in = next((interface.symbol["massflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), None)
            self.c_out = next((interface.symbol["massflow"] for interface in self.interfaces_out if interface.connection_from_id == 2), None)

            self.c_PFR = SymbTerminalNode(self.name + "_c_PFR","m." + self.name + "_c_PFR[i,V_PFR]",['i','V_PFR'],None,None)

            self.V_dot = next((interface.symbol["volumeflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), None)
            self.V_dot_out = next((interface.symbol["volumeflow"] for interface in self.interfaces_out if interface.connection_from_id == 2), None)

            self.dcdV = SymbTerminalNode(self.name + "_dcdV","m." + self.name + "_dcdV[i,V_PFR]",["i","V_PFR"], [self.c_PFR.unique_representation],["V_PFR"])

            self.math.equal_isolo = BinaryOperator("=", "==", ['i']) # equation index only applies to =
            self.math.equal_i_VPFR = BinaryOperator("=", "==", ['i','V_PFR']) # equation index only applies to =
            self.math.indexm1 = UnaryOperator("indexm1","indexm1",None)
            self.math.indexPFR0 = UnaryOperator("indexPFR0","indexPFR0",None)

            self.state = [self.V_dot,self.dcdV,self.math.multi,getattr(self,"ap_reactionR"),self.math.equal_i_VPFR]

            self.state.extend([self.V_dot,self.V_dot_out,self.math.equal_noind])
            self.state.extend([self.c_out,self.c_PFR,self.math.indexm1,self.math.equal_isolo])

            self.state.extend([self.c_PFR,self.math.indexPFR0,self.c_in,self.math.equal_isolo])

            self.c_out.status = "var_constitutiveequation"
            self.V_dot_out.status = "var_constitutiveequation"
            self.c_PFR.status = "var_constitutiveequation"
        
        return True

class VALVE(Interface):
    
    def __init__(self, name, modus):
        super().__init__(name)
        self.type = "convection"
        self.color = 2

        if modus == "normal":

            self.F_conv = SymbTerminalNode(self.name + "_F_conv","m." + self.name + "_F_conv[i,n]",['i','n'],None,None,lb=0,ub=100)
            self.V_dot_conv = SymbTerminalNode(self.name + "_V_dot_conv","m." + self.name + "_V_dot_conv[n]",['n'],None,None,lb=1e-6,ub=100)

            self.symbol["massflow"] = self.F_conv
            self.symbol["volumeflow"] = self.V_dot_conv

        if modus == "rtd":
            
            self.c_conv = SymbTerminalNode(self.name + "_c_conv","m." + self.name + "_c_conv[t]",['t'],None,None,lb=0,ub=1)
            self.V_dot_conv = SymbTerminalNode(self.name + "_V_dot_conv","m." + self.name + "_V_dot_conv",None,None,None,lb=1e-6,ub=1)

            self.symbol["massflow"] = self.c_conv
            self.symbol["volumeflow"] = self.V_dot_conv

        if modus == "hierarchic_data":
            
            self.c_conv = SymbTerminalNode(self.name + "_c_conv","m." + self.name + "_c_conv[i]",['i'],None,None,lb=0,ub=1)
            self.V_dot_conv = SymbTerminalNode(self.name + "_V_dot_conv","m." + self.name + "_V_dot_conv",None,None,None,lb=1e-6,ub=1)

            self.symbol["massflow"] = self.c_conv
            self.symbol["volumeflow"] = self.V_dot_conv

    def generate_state(self, modus):
        # self.c_conv = SymbTerminalNode(self.name + "_c_conv","m." + self.name + "_c_conv[i]",['i'],None,None,lb=0,ub=100) # because created unter rtd modus
        # self.V_dot_conv = SymbTerminalNode(self.name + "_V_dot_conv","m." + self.name + "_V_dot_conv",None,None,None,lb=1e-6,ub=1)

        if modus == "rtd" or modus == "hierarchic_data":
            self.symbol["massflow"] = self.c_conv
            self.symbol["volumeflow"] = self.V_dot_conv
        else:
            self.symbol["massflow"] = self.F_conv
            self.symbol["volumeflow"] = self.V_dot_conv

        self.state = []
        return True

class FILM(Interface):
    
    def __init__(self, name, modus):
        super().__init__(name)
        self.type = "diffusion"
        self.color = 3

        if modus == "normal":

            self.J_diff = SymbTerminalNode(self.name + "_J_diff","m." + self.name + "_J_diff[i,n]",['i','n'],None,None,lb=-1,ub=1)
            self.A = SymbTerminalNode(self.name + "_A", "m." + self.name + "_A[n]", ['n'], None, None, lb=0, ub=100000000000)
            self.Pv = SymbTerminalNode(self.name + "_Pv", "m." + self.name + "_Pv[n]", ['n'], None, None, lb=0.1, ub=10000)

            self.symbol["massflow"] = self.J_diff
            self.symbol["surface"] = self.A
            self.symbol["energyflow"] = self.Pv

        self.Tc = None

    def phenomenon_qualifier(self,type):
        if type == "diffusion":
            return True
        else:
            return False

    def generate_state(self, modus):
        self.state = []
        return True

class MIX(Compartment):

    def __init__(self, name):
        super().__init__(name)
        self.type = "MIX"
        self.color = 4

        self.connections = [{"connection_type":VALVE, "direction":"in", "id": 1},
                            {"connection_type":VALVE, "direction":"in", "id": 2},
                            {"connection_type":VALVE, "direction":"out", "id": 3},
                            ]
        
    def generate_state(self, modus):
        
        if modus == "normal":

            self.F_in1 = next((interface.symbol["massflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), NumTerminalNode("0","0"))
            self.F_in2 = next((interface.symbol["massflow"] for interface in self.interfaces_in if interface.connection_to_id == 2), NumTerminalNode("0","0"))
            self.F_out = next((interface.symbol["massflow"] for interface in self.interfaces_out if interface.connection_from_id == 3), None)

            self.V_dot_in1 = next((interface.symbol["volumeflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), NumTerminalNode("0","0"))
            self.V_dot_in2 = next((interface.symbol["volumeflow"] for interface in self.interfaces_in if interface.connection_to_id == 2), NumTerminalNode("0","0"))
            self.V_dot_out = next((interface.symbol["volumeflow"] for interface in self.interfaces_out if interface.connection_from_id == 3), None)

            self.state = [self.F_out,self.F_in1,self.F_in2,self.math.plus,self.math.equal_i,self.V_dot_out,self.V_dot_in1,self.V_dot_in2,self.math.plus,self.math.equal_i]
            
            self.F_out.status = "var_constitutiveequation"
            self.V_dot_out.status = "var_constitutiveequation"

        if modus == "rtd":

            self.c_in1 = next((interface.symbol["massflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), None)
            self.c_in2 = next((interface.symbol["massflow"] for interface in self.interfaces_in if interface.connection_to_id == 2), None)
            self.c_out = next((interface.symbol["massflow"] for interface in self.interfaces_out if interface.connection_from_id == 3), None)

            self.V_dot_in1 = next((interface.symbol["volumeflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), NumTerminalNode("0","0"))
            self.V_dot_in2 = next((interface.symbol["volumeflow"] for interface in self.interfaces_in if interface.connection_to_id == 2), NumTerminalNode("0","0"))
            self.V_dot_out = next((interface.symbol["volumeflow"] for interface in self.interfaces_out if interface.connection_from_id == 3), None)

            self.state = [self.c_out,self.V_dot_out,self.math.multi,self.c_in1,self.V_dot_in1,self.math.multi,self.c_in2,self.V_dot_in2,self.math.multi,self.math.plus,self.math.equal_t,
                          self.V_dot_out,self.V_dot_in1,self.V_dot_in2,self.math.plus,self.math.equal_noind]

            self.c_out.status = "var_constitutiveequation"
            self.V_dot_out.status = "var_constitutiveequation"

        if modus == "hierarchic_data":

            self.c_in1 = next((interface.symbol["massflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), None)
            self.c_in2 = next((interface.symbol["massflow"] for interface in self.interfaces_in if interface.connection_to_id == 2), None)
            self.c_out = next((interface.symbol["massflow"] for interface in self.interfaces_out if interface.connection_from_id == 3), None)

            self.V_dot_in1 = next((interface.symbol["volumeflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), NumTerminalNode("0","0"))
            self.V_dot_in2 = next((interface.symbol["volumeflow"] for interface in self.interfaces_in if interface.connection_to_id == 2), NumTerminalNode("0","0"))
            self.V_dot_out = next((interface.symbol["volumeflow"] for interface in self.interfaces_out if interface.connection_from_id == 3), None)

            self.math.equal_isolo = BinaryOperator("=", "==", ['i']) # equation index only applies to =

            self.state = [self.c_out,self.V_dot_out,self.math.multi,self.c_in1,self.V_dot_in1,self.math.multi,self.c_in2,self.V_dot_in2,self.math.multi,self.math.plus,self.math.equal_isolo,
                          self.V_dot_out,self.V_dot_in1,self.V_dot_in2,self.math.plus,self.math.equal_noind]

            self.c_out.status = "var_constitutiveequation"
            self.V_dot_out.status = "var_constitutiveequation"

        return True

class SPLIT(Compartment):

    def __init__(self, name):
        super().__init__(name)
        self.type = "SPLIT"
        self.color = 6

        self.connections = [{"connection_type":VALVE, "direction":"in", "id": 1},
                            {"connection_type":VALVE, "direction":"out", "id": 2},
                            {"connection_type":VALVE, "direction":"out", "id": 3},
                            ]
        
    def generate_state(self, modus):
        
        if modus == "rtd":

            self.c_in = next((interface.symbol["massflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), None)
            self.c_out1 = next((interface.symbol["massflow"] for interface in self.interfaces_out if interface.connection_from_id == 2), None)
            self.c_out2 = next((interface.symbol["massflow"] for interface in self.interfaces_out if interface.connection_from_id == 3), None)

            self.V_dot_in = next((interface.symbol["volumeflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), NumTerminalNode("0","0"))
            self.V_dot_out1 = next((interface.symbol["volumeflow"] for interface in self.interfaces_out if interface.connection_from_id == 2), NumTerminalNode("0","0"))
            self.V_dot_out2 = next((interface.symbol["volumeflow"] for interface in self.interfaces_out if interface.connection_from_id == 3), None)

            self.state = [self.c_out1,self.c_in,self.math.equal_t,self.c_out2,self.c_in,self.math.equal_t,
                          self.V_dot_in,self.V_dot_out1,self.V_dot_out2,self.math.plus,self.math.equal_noind]

            self.c_out1.status = "var_constitutiveequation"
            self.c_out2.status = "var_constitutiveequation"
            self.V_dot_out1.status = "var_constitutiveequation"
            self.V_dot_out2.status = "var_constitutiveequation"

        if modus == "hierarchic_data":

            self.c_in = next((interface.symbol["massflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), None)
            self.c_out1 = next((interface.symbol["massflow"] for interface in self.interfaces_out if interface.connection_from_id == 2), None)
            self.c_out2 = next((interface.symbol["massflow"] for interface in self.interfaces_out if interface.connection_from_id == 3), None)

            self.V_dot_in = next((interface.symbol["volumeflow"] for interface in self.interfaces_in if interface.connection_to_id == 1), NumTerminalNode("0","0"))
            self.V_dot_out1 = next((interface.symbol["volumeflow"] for interface in self.interfaces_out if interface.connection_from_id == 2), NumTerminalNode("0","0"))
            self.V_dot_out2 = next((interface.symbol["volumeflow"] for interface in self.interfaces_out if interface.connection_from_id == 3), None)

            self.math.equal_isolo = BinaryOperator("=", "==", ['i']) # equation index only applies to =

            self.state = [self.c_out1,self.c_in,self.math.equal_isolo,self.c_out2,self.c_in,self.math.equal_isolo,
                          self.V_dot_in,self.V_dot_out1,self.V_dot_out2,self.math.plus,self.math.equal_noind]

            self.c_out1.status = "var_constitutiveequation"
            self.c_out2.status = "var_constitutiveequation"

            if isinstance(self.interfaces_out[0].compartment_to,MIX) and isinstance(self.interfaces_out[1].compartment_to,MIX):
                self.V_dot_out1.status = "var_constitutiveequation"
                self.V_dot_out2.status = "var_constitutiveequation"

        return True
    
def get_building_blocks(case_study):
    # Select the available building blocks for the graph generation

    ### CASE STUDY
    if case_study == "insilico-ptc":
        compartment_blocks = [CSTR]
        interface_blocks = [VALVE, FILM]
    elif case_study == "rtd":
        compartment_blocks = [CSTR,PFR,SPLIT,MIX]
        interface_blocks = [VALVE]

    building_blocks = (compartment_blocks,interface_blocks)
    return building_blocks