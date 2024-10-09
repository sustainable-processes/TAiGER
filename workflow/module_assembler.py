from object_library import *
from classes_state_representation import *
import copy

class AssemblerModule:

    def __init__(self, topology, phenomena):
        self.topology = copy.deepcopy(topology)
        self.phenomena = copy.deepcopy(phenomena)

    def get_phenomenon(self, identifier : str):
        _phenomenon = None
        for phenomenon in self.phenomena:
            if phenomenon.identifier == identifier:
                _phenomenon = phenomenon
        return _phenomenon

    def clean_topology(self):
        # Deletes some excessive dummy compartments that might have been left over from the graph generation process
        new_compartments = []
        for compartment in self.topology.compartments:
            if not compartment.is_dummy:
                new_compartments.append(compartment)
        new_interfaces = []
        for interface in self.topology.interfaces:
            if not (interface.compartment_from.is_dummy or interface.compartment_to.is_dummy):
                new_interfaces.append(interface)
        self.topology.compartments = new_compartments
        self.topology.interfaces = new_interfaces

        for compartment in self.topology.compartments:
            new_interfaces = []
            for interface in compartment.interfaces_in:
                if not (interface.compartment_from.is_dummy or interface.compartment_to.is_dummy):
                    new_interfaces.append(interface)
            compartment.interfaces_in = new_interfaces
            new_interfaces = []
            for interface in compartment.interfaces_out:
                if not (interface.compartment_from.is_dummy or interface.compartment_to.is_dummy):
                    new_interfaces.append(interface)
            compartment.interfaces_out = new_interfaces
    
    def assign_phenomena(self, modus):
        # Decision rules on how the phenomena are distributed among the building blocks of a given topology
        ### An alternative would be to connect the phenomena to the building blocks a priori, which would be much nicer

        # Catch erroneous topologies (do not exist usually)
        for compartment in self.topology.compartments:
            if len(compartment.interfaces_in) == 0 or len(compartment.interfaces_out) == 0:
                return -1
        
        if modus == "normal":
            
            # For the first case study, the phase phenomena are assigned based on the initial flows that correspond to the real-life streams
            ## This is rather ugly here and (very rarely) leads to erroneous topologies
            for compartment in self.topology.compartments:
                if not compartment.is_environment:
                    if next((interface.is_envflow_out for interface in compartment.interfaces_in if interface.connection_from_id == 1), False):
                        compartment.phenomena.append(self.get_phenomenon("phase1"))
                    if next((interface.is_envflow_out for interface in compartment.interfaces_in if interface.connection_from_id == 2), False):
                        compartment.phenomena.append(self.get_phenomenon("phase2"))
            for i in range(0,3):
                for compartment in self.topology.compartments:
                    if not compartment.is_environment:
                        for interface in compartment.interfaces_in:
                            if type(interface)==VALVE:
                                if not interface.compartment_from.is_environment:
                                    # if len(compartment.phenomena) == 0: # see above
                                    if not len(interface.compartment_from.phenomena) == 0:
                                        if not interface.compartment_from.phenomena[0] in compartment.phenomena:
                                            compartment.phenomena.extend(interface.compartment_from.phenomena)

            for interface in self.topology.interfaces:
                if type(interface) == VALVE:
                    interface.phenomena.append(self.get_phenomenon("convection"))
                if type(interface) == FILM:
                    interface.phenomena.append(self.get_phenomenon("film_masstransfer"))

        # For the RTD + data integration, each reactor hosts the esterification reaction
        if modus == "hierarchic_data":

            for compartment in self.topology.compartments:
                if type(compartment) == CSTR or type(compartment) == PFR:
                    compartment.phenomena.append(self.get_phenomenon("ap_reaction"))

    def generate_state(self, modus):
        # Set global variables (should be moved to a better place, e.g., the environment building block)
        for interface in self.topology.interfaces:
            interface.generate_state(modus)

            if modus == "normal":
                interface.Tc = self.topology.compartments[0].Tc

        for compartment in self.topology.compartments:
            compartment.generate_state(modus)

            if modus == "normal":
                compartment.Tc = self.topology.compartments[0].Tc
            if modus == "hierarchic_data":
                compartment.T = self.topology.compartments[0].T

        self.state = []
        
        # Compile all equations to one equation system that acts as the state for the equation generator
        for compartment in self.topology.compartments:
            self.state += compartment.state
        for interface in self.topology.interfaces:
            self.state += interface.state

    # Compile equation libraries from all phenomena from all compartments and interfaces
    def generate_eqlib(self, modus):
        self.eq_library = {}
        self.exclusive_eqs = []
        for compartment in self.topology.compartments:
            if len(compartment.phenomena) > 0:
                compartment.compile_libraries()
                self.eq_library = self.eq_library | compartment.eq_library
                self.exclusive_eqs += compartment.exclusive_eqs
        for interface in self.topology.interfaces:
            interface.compile_libraries()
            self.eq_library = self.eq_library | interface.eq_library
                    
    def generate_knownvals(self, input_profile, modus):
        # Very elaborate way to perform very simple renaming of known parameters and to assign them to the correct places
        self.known_values = {}
        for compartment in self.topology.compartments:
            compartment_known_values = []
            for known_value in input_profile["known_values"]:
                if known_value["target"] == compartment.name:
                    compartment_known_values.append(known_value)
                if len(compartment.phenomena) > 0:
                    for phenomenon in compartment.phenomena:
                        if known_value["target"] == phenomenon.identifier:
                            compartment_known_values.append(known_value)
            for known_value in compartment_known_values:
                if known_value["target"] == "ap_reaction":
                    self.known_values["ap_reaction_" + known_value["variable"]] = known_value["value"] # Workaround for global phenomena of ap reaction
                else:
                    self.known_values[compartment.name + "_" + known_value["variable"]] = known_value["value"]

        for interface in self.topology.interfaces:
            interface_known_values = []
            for known_value in input_profile["known_values"]:
                if known_value["target"] == interface.name:
                    interface_known_values.append(known_value)
                if known_value["target"] == "envflow" + str(interface.connection_from_id) and interface.is_envflow_out:
                    known_value["target"] = interface.name
                    interface_known_values.append(known_value)
                if len(interface.phenomena) > 0:
                    for phenomenon in interface.phenomena:
                        if known_value["target"] == phenomenon.identifier:
                            interface_known_values.append(known_value)
            for known_value in interface_known_values:
                self.known_values[interface.name + "_" + known_value["variable"]] = known_value["value"]
        
        self.known_values["measured_var"] = []
        self.known_values["measured_var_index"] = []
        for var in input_profile["measured_var"]:
            for interface in self.topology.interfaces:
                if var["target"] == "envflow" + str(interface.connection_to_id) and interface.is_envflow_in:
                    var["target"] = interface.name
            self.known_values["measured_var"].append({var["target"] + "_" + var["variable"]:var["value"]})
            self.known_values["measured_var_index"].append({var["target"] + "_" + var["variable"]:var["index"]})

        self.known_values["manipulated_var"] = []
        for var in input_profile["manipulated_var"]:
            for interface in self.topology.interfaces:
                if var["target"] == "envflow" + str(interface.connection_from_id) and interface.is_envflow_out:
                    var["target"] = interface.name
            self.known_values["manipulated_var"].append({var["target"] + "_" + var["variable"]:var["value"]})
        
        self.known_values["sets"] = input_profile["sets"]
        self.known_values["n_exp"] = input_profile["n_exp"]

        if modus == "rtd":
            self.known_values["input_function"] = input_profile["input_function"]
        
    def print_state(self):
        readable_state = [sym.unique_representation for sym in self.state]
        print(readable_state)

    def trace_volume(self, modus):
        # Add global volume balances
        ## Should be moved to the environment building block as well
        if modus == "normal":
            V_total = NumTerminalNode("V_total","0.105e5")
            equal = BinaryOperator("=", "==", ['n'])
            plus = BinaryOperator("+", "+", None)

            volume_balance = [V_total]
            for compartment in self.topology.compartments:
                if isinstance(compartment,CSTR) or isinstance(compartment,PFR):
                    volume_balance.append(compartment.V)
                    # compartment.V.status = "var_constitutiveequation"
            for compartment in self.topology.compartments:
                if isinstance(compartment,CSTR) or isinstance(compartment,PFR):
                    volume_balance.append(plus)
            volume_balance[-1] = equal
            if len(volume_balance) > 1: # no CSTRs
                self.state += volume_balance

            value_phi = 1.2748/(1.2748+1.65)
            phi = NumTerminalNode("phi", str(value_phi))
            equal = BinaryOperator("=", "==", ['n'])
            plus = BinaryOperator("+", "+", None)
            multi = BinaryOperator("*", "*", None)
            total_phi = [phi,V_total,multi]
            for compartment in self.topology.compartments:
                if isinstance(compartment,CSTR) or isinstance(compartment,PFR):
                    if any(phenomenon.identifier == "phase1" for phenomenon in compartment.phenomena) and len([phenomenon for phenomenon in compartment.phenomena if "phase" in phenomenon.identifier]) != 2:
                        total_phi.append(compartment.V)
            for compartment in self.topology.compartments:
                if isinstance(compartment,CSTR) or isinstance(compartment,PFR):
                    if any(phenomenon.identifier == "phase1" for phenomenon in compartment.phenomena) and len([phenomenon for phenomenon in compartment.phenomena if "phase" in phenomenon.identifier]) != 2:
                        total_phi.append(plus)
            total_phi[-1] = equal
            if len(total_phi) > 3: # no CSTRs
                self.state += total_phi

            for compartment in self.topology.compartments:
                if isinstance(compartment,CSTR) or isinstance(compartment,PFR):
                    if not any(isinstance(interface,FILM) for interface in compartment.interfaces_in + compartment.interfaces_out):
                        compartment.V.status = "var_constitutiveequation"

        if modus == "rtd":
            V_total_lb = NumTerminalNode("V_total","16")
            V_total_ub = NumTerminalNode("V_total","19")
            equal = BinaryOperator("=", "==", None)
            geq = BinaryOperator(">=",">=",None)
            leq = BinaryOperator("<=","<=",None)
            plus = BinaryOperator("+", "+", None)
            
            volume_balance = [V_total_lb]
            for compartment in self.topology.compartments:
                if isinstance(compartment,CSTR) or isinstance(compartment,PFR):
                    volume_balance.append(compartment.V)
                    # compartment.V.status = "var_constitutiveequation"
            for compartment in self.topology.compartments:
                if isinstance(compartment,CSTR) or isinstance(compartment,PFR):
                    volume_balance.append(plus)
            volume_balance[-1] = leq
            if len(volume_balance) > 1: # no CSTRs
                self.state += volume_balance

            volume_balance = [V_total_ub]
            for compartment in self.topology.compartments:
                if isinstance(compartment,CSTR) or isinstance(compartment,PFR):
                    volume_balance.append(compartment.V)
                    # compartment.V.status = "var_constitutiveequation"
            for compartment in self.topology.compartments:
                if isinstance(compartment,CSTR) or isinstance(compartment,PFR):
                    volume_balance.append(plus)
            volume_balance[-1] = geq
            if len(volume_balance) > 1: # no CSTRs
                self.state += volume_balance