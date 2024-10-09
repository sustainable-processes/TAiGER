from classes_compartment_representation import *
from object_library import *
from module_input import *
import pandas as pd
import numpy as np

class CompartmentalizationModule:

    def __init__(self):
        self.topology = None
        self.current_trajectory = []

    def initialize_topology(self, case_study, building_blocks, modus):
        input_module = InputModule()
        self.topology = input_module.initialize_topology(case_study, building_blocks, modus)

    def get_actions(self, it, case_study):
            # Collect all possible graph manipulations
            action_list_insert = []
            action_list_terminate = []

            # Episode length (see descriptions of case studies in thesis)
            if case_study == "insilico-ptc":
                e_len = 10
            elif case_study == "rtd":
                e_len = 20

            # Graph production rules (TODO: parse rules from ontology)
            if it <= e_len:
                for interface in self.topology.interfaces:
                    if not (interface.compartment_from.is_dummy or interface.compartment_to.is_dummy):
                        if type(interface) == VALVE:
                            for building_block in self.topology.building_blocks[0]:
                                if building_block == CSTR or (building_block == PFR and not any([isinstance(compartment,PFR) for compartment in self.topology.compartments]) and any([isinstance(compartment,CSTR) for compartment in self.topology.compartments])):
                                    action_list_insert.append({"action_type": "insert_compartment", "building_block": building_block, "target": interface.identifier})

                if MIX in self.topology.building_blocks[0] and SPLIT in self.topology.building_blocks[0]:
                    for interface in self.topology.interfaces:
                        if not (interface.compartment_from.is_dummy or interface.compartment_to.is_dummy):
                            if type(interface) == VALVE:
                                action_list_insert.append({"action_type": "insert_compartment", "building_block": "SPLIT-MIX", "target": interface.identifier})

            # The trajectory can be terminated prematurely, if no production is applicable or 15 iterations have been exceeded
            if it > (e_len-5) or (len(action_list_insert)==0):
                action_list_terminate.append({"action_type": "terminate"})

            return [action_list_insert,action_list_terminate]
    
    def choose_action(self, epsilon: float, available_actions: list, Q: pd.DataFrame) -> dict:
        p = np.random.random()
        Q_filtered = Q[Q["state"].apply(lambda x: x == self.topology.canonical_form)] # Only contains actions previously made in the same state
        if p < epsilon: # With probability of epsilon, pick random action from available actions for current state.
            print("Random step.")
            p_basic_decision = np.random.randint(0,len(available_actions))
            while len(available_actions[p_basic_decision]) == 0:
                p_basic_decision = np.random.randint(0,len(available_actions))
            chosen_action = available_actions[p_basic_decision][np.random.choice(len(available_actions[p_basic_decision]))]
        else: # With probability of 1-epsilon, pick action with largest Q(s,a) value for current state.
            Q_filtered = Q[Q["state"].apply(lambda x: x == self.topology.canonical_form)] 
            if len(Q_filtered) > 0:
                print("Learned step.")
                index_of_Qmax = Q_filtered["Q(s,a)"].idxmax()
                chosen_action = Q_filtered.at[index_of_Qmax, "action"]
            else:
                # We also choose a random step if no applicable state-action pair could be found in the Q-table
                print("Random step.")
                p_basic_decision = np.random.randint(0,len(available_actions))
                while len(available_actions[p_basic_decision]) == 0:
                    p_basic_decision = np.random.randint(0,len(available_actions))
                chosen_action = available_actions[p_basic_decision][np.random.choice(len(available_actions[p_basic_decision]))]

        
        return chosen_action


    def step(self, chosen_action, modus):
        # Actually apply the chosen graph production to the topology

        if chosen_action["action_type"] == "insert_compartment":

            if chosen_action["building_block"] == "SPLIT-MIX":
                old_interface = self.topology.get_object(chosen_action["target"])
                new_compartment1 = SPLIT("compartment" + str(self.topology.compartment_counter))
                self.topology.add_compartment(new_compartment1)
                new_compartment2 = MIX("compartment" + str(self.topology.compartment_counter))
                self.topology.add_compartment(new_compartment2)

                ObjectClass = type(old_interface)
                new_interface1 = ObjectClass("interface" + str(self.topology.interface_counter), modus)
                self.topology.add_interface(new_interface1)
                new_interface2 = ObjectClass("interface" + str(self.topology.interface_counter), modus)
                self.topology.add_interface(new_interface2)
                new_interface3 = ObjectClass("interface" + str(self.topology.interface_counter), modus)
                self.topology.add_interface(new_interface3)
                new_interface4 = ObjectClass("interface" + str(self.topology.interface_counter), modus)
                self.topology.add_interface(new_interface4)

                new_interface1.is_envflow_out = old_interface.is_envflow_out

                new_interface1.compartment_from = old_interface.compartment_from
                new_interface1.connection_from_id = old_interface.connection_from_id
                new_interface1.compartment_to = new_compartment1
                for connection in new_compartment1.connections:
                    if connection["connection_type"] == type(old_interface) and connection["direction"] == "in":
                        new_interface1.connection_to_id = connection["id"]

                new_interface1.compartment_from.interfaces_out.append(new_interface1)
                new_interface1.compartment_to.interfaces_in.append(new_interface1)

                new_interface1.is_open = False


                new_interface4.is_envflow_in = old_interface.is_envflow_in

                new_interface4.compartment_to = old_interface.compartment_to
                new_interface4.connection_to_id = old_interface.connection_to_id
                new_interface4.compartment_from = new_compartment2
                for connection in new_compartment2.connections:
                    if connection["connection_type"] == type(old_interface) and connection["direction"] == "out":
                        new_interface4.connection_from_id = connection["id"]

                new_interface4.compartment_from.interfaces_out.append(new_interface4)
                new_interface4.compartment_to.interfaces_in.append(new_interface4)

                new_interface4.is_open = False

                new_interface2.compartment_from = new_compartment1
                new_interface2.connection_from_id = new_compartment1.interface_type_qualifier()[0]["id"]
                new_interface2.compartment_to = new_compartment2
                new_interface2.connection_to_id = new_compartment2.interface_type_qualifier()[0]["id"]

                new_interface3.compartment_from = new_compartment1
                new_interface3.connection_from_id = new_compartment1.interface_type_qualifier()[1]["id"]
                new_interface3.compartment_to = new_compartment2
                new_interface3.connection_to_id = new_compartment2.interface_type_qualifier()[1]["id"]

                new_compartment1.interfaces_out.append(new_interface2)
                new_compartment1.interfaces_out.append(new_interface3)
                new_compartment2.interfaces_in.append(new_interface2)
                new_compartment2.interfaces_in.append(new_interface3)

                old_interface.compartment_from.interfaces_out.remove(old_interface)
                old_interface.compartment_to.interfaces_in.remove(old_interface)

                self.topology.interfaces.remove(old_interface)

            else:

                ObjectClass = chosen_action["building_block"]
                old_interface = self.topology.get_object(chosen_action["target"])

                new_compartment = ObjectClass("compartment" + str(self.topology.compartment_counter))

                ObjectClass = type(old_interface)
                new_interface1 = ObjectClass("interface" + str(self.topology.interface_counter), modus)
                self.topology.add_interface(new_interface1)
                new_interface2 = ObjectClass("interface" + str(self.topology.interface_counter), modus)
                self.topology.add_interface(new_interface2)

                new_interface1.is_envflow_out = old_interface.is_envflow_out
                new_interface2.is_envflow_in = old_interface.is_envflow_in

                new_interface1.compartment_from = old_interface.compartment_from
                new_interface1.connection_from_id = old_interface.connection_from_id
                new_interface1.compartment_to = new_compartment
                for connection in new_compartment.connections:
                    if connection["connection_type"] == type(old_interface) and connection["direction"] == "in":
                        new_interface1.connection_to_id = connection["id"]

                new_interface2.compartment_from = new_compartment
                new_interface2.compartment_to = old_interface.compartment_to
                new_interface2.connection_to_id = old_interface.connection_to_id
                for connection in new_compartment.connections:
                    if connection["connection_type"] == type(old_interface) and connection["direction"] == "out":
                        new_interface2.connection_from_id = connection["id"]

                new_interface1.compartment_from.interfaces_out.append(new_interface1)
                new_interface1.compartment_to.interfaces_in.append(new_interface1)
                new_interface2.compartment_from.interfaces_out.append(new_interface2)
                new_interface2.compartment_to.interfaces_in.append(new_interface2)

                new_interface1.is_open = False
                new_interface2.is_open = False

                old_interface.compartment_from.interfaces_out.remove(old_interface)
                old_interface.compartment_to.interfaces_in.remove(old_interface)

                self.topology.interfaces.remove(old_interface)
                self.topology.add_compartment(new_compartment)

                optional_connections = new_compartment.interface_type_qualifier()
                for connection in optional_connections:
                    ObjectClass = connection["connection_type"]
                    new_interface = ObjectClass("interface" + str(self.topology.interface_counter), modus)
                    new_interface.is_open = True
                    new_interface.is_optional = True
                    if connection["direction"] == "in":
                        new_interface.compartment_to = new_compartment
                        new_interface.connection_to_id = connection["id"]
                        new_compartment.interfaces_in.append(new_interface)
                        dummy_compartment = Compartment("dummy" + str(self.topology.compartment_counter))
                        dummy_compartment.is_dummy = True
                        new_interface.compartment_from = dummy_compartment
                    if connection["direction"] == "out":
                        new_interface.compartment_from = new_compartment
                        new_interface.connection_from_id = connection["id"]
                        new_compartment.interfaces_out.append(new_interface)
                        dummy_compartment = Compartment("dummy" + str(self.topology.compartment_counter))
                        dummy_compartment.is_dummy = True
                        new_interface.compartment_to = dummy_compartment
                    self.topology.add_compartment(dummy_compartment)
                    self.topology.add_interface(new_interface)

        if chosen_action["action_type"] == "terminate":
            interfaces_to_be_deleted = []
            compartments_to_be_deleted = []
            for interface in self.topology.interfaces:
                if interface.compartment_to.is_dummy:
                    compartments_to_be_deleted.append(interface.compartment_to)
                    interfaces_to_be_deleted.append(interface)
                if interface.compartment_from.is_dummy:
                    compartments_to_be_deleted.append(interface.compartment_from)
                    interfaces_to_be_deleted.append(interface)

            for interface in interfaces_to_be_deleted:
                self.topology.interfaces.remove(interface)
            for compartment in compartments_to_be_deleted:
                self.topology.compartments.remove(compartment)

            self.topology.completed = True

        # Post-process and canonize the changed topology
        self.topology.get_object_colors()
        self.topology.get_canon_labels()
        self.topology.get_canon_trace()
        self.topology.find_disconnecting_pairs()