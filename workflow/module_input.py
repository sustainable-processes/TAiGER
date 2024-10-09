import pandas as pd

from classes_compartment_representation import *
from object_library import *

class InputModule():

    def generate_input_profile(self, case_study, modus) -> dict:
        
        if case_study == "insilico-ptc":

            # Name and index of measured variable
            measured_var = [{"target":"envflow4","variable":"F_conv","index":5},
                            {"target":"envflow4","variable":"F_conv","index":6}]

            manipulated_var = [{"target":"environment", "variable":"Tc"}]
            n_exp = 6
            
            input_profile = {}
            input_profile["sets"] = {
                    'i':{'min': 1, 'max': 6, 'type': 'discrete', 'description': "indexes components"}, 
                    'p':{'min': 1, 'max': 1, 'type': 'discrete', 'description': "indexes reactions"},
                    'n':{'min': 1, 'max': n_exp, 'type': 'discrete', 'description': "indexes experiments"}
                    }
            
            input_profile["known_values"] = [
                            {"target":"envflow1", "variable":"F_conv", "value":{1:0,2:0.000125823e5,3:0,4:0.000544085e5,5:0,6:0}},
                            {"target":"envflow2", "variable":"F_conv", "value":{1:1.01805e-1,2:0,3:0,4:0,5:0.00013464e5,6:0}},
                            {"target":"envflow1", "variable":"V_dot_conv", "value":1.2748},
                            {"target":"envflow2", "variable":"V_dot_conv", "value":1.65},
                            {"target":"film_masstransfer", "variable":"H", "value":{1:0.1,2:1,3:0.1,4:0.0034,5:0,6:0}},
                            {"target":"phase1", "variable":"MVp", "value":584.4},
                            {"target":"phase1", "variable":"MV", "value":189},
                            {"target":"phase1", "variable":"Pp", "value":1141},
                            {"target":"phase1", "variable":"Pl", "value":357.9},
                            {"target":"phase2", "variable":"MVp", "value":584.4},
                            {"target":"phase2", "variable":"MV", "value":189},
                            {"target":"phase2", "variable":"Pp", "value":1141},
                            {"target":"phase2", "variable":"Pl", "value":357.9},
                            {"target":"film_masstransfer", "variable":"d", "value":0.17},
                            {"target":"film_masstransfer", "variable":"N", "value":1000},
                            {"target":"film_masstransfer", "variable":"dp", "value":1e-5},
                            {"target":"phase1", "variable":"k0_aq", "value":{1:0.0126092}},
                            {"target":"phase1", "variable":"E_aq", "value":{1:70111}},
                            {"target":"phase1", "variable":"Tref_aq", "value":{1:317.3}},
                            {"target":"phase1", "variable":"nu_ip_aq", "value":{(1,1): -1, (2,1): -1, (3,1): 1, (4,1): 1, (5,1): 0, (6,1):0}},
                            {"target":"phase1", "variable":"ord_ip_aq", "value":{(1,1): 1, (2,1): 1, (3,1): 0, (4,1): 0, (5,1): 0, (6,1):0}},
                            {"target":"phase2", "variable":"k0_org", "value":{1:0.1}},
                            {"target":"phase2", "variable":"E_org", "value":{1:43024.2}},
                            {"target":"phase2", "variable":"Tref_org", "value":{1:317.3}},
                            {"target":"phase2", "variable":"nu_ip_org", "value":{(1,1): 1, (2,1): 0, (3,1): -1, (4,1): 0, (5,1): -1, (6,1):1}},
                            {"target":"phase2", "variable":"ord_ip_org", "value":{(1,1): 0, (2,1): 0, (3,1): 1, (4,1): 0, (5,1): 1, (6,1):0}},
                            {"target":"phase1", "variable":"kL_discr", "value":{1: 1, 2: 0, 3: 1, 4: 1, 5: 0, 6: 0}},
                            {"target":"phase2", "variable":"kL_discr", "value":{1: 1, 2: 0, 3: 1, 4: 1, 5: 0, 6: 0}},
                            {"target":"film_masstransfer", "variable":"kL_discr", "value":{1: 1, 2: 0, 3: 1, 4: 1, 5:0, 6:0}},
                            ]

            input_data = pd.read_csv('./workflow/inputs/input_data_insilico-ptc.csv')

            # Process input data so we can use the values within the parameter estimation
            input_profile["manipulated_var"] = []
            for index, var in enumerate(manipulated_var):
                var["value"] = {n: mani for n, mani in zip(range(1,n_exp+1), input_data[manipulated_var[index]["variable"]].tolist())}
                input_profile["manipulated_var"].append(manipulated_var[index])

            input_profile["measured_var"] = []
            for index, var in enumerate(measured_var):
                var["value"] = {n: meas for n, meas in zip(range(1,n_exp+1), input_data[measured_var[index]["variable"]+"["+str(measured_var[index]["index"])+"]"].tolist())}
                input_profile["measured_var"].append(measured_var[index])

            input_profile["n_exp"] = n_exp

            return input_profile
            
        if case_study == "tcr-rtd":

            if modus == "rtd":

                # Name and index of measured variable
                measured_var = [{"target":"envflow2","variable":"c_conv","index":999}]

                manipulated_var = [{"target":"envflow1", "variable":"c_conv"}]

                n_exp = 48
                
                input_profile = {}
                input_profile["sets"] = {
                        't':{'min': 0, 'max': 51, 'type': 'continuous', 'description': "indexes time"}, # 51 = max(data)/time_norm_granularity  
                        'tau':{'min':0, 'max':15, 'type': 'discrete', 'description': "tau"}
                        }
                
                input_profile["known_values"] = [
                                {"target":"envflow1", "variable":"V_dot_conv", "value":17/60*3.235726},
                                ]

                input_data = pd.read_csv('./workflow/inputs/MB_MeCN_8.50ml_360rpm_rtd.csv', delimiter=";")

                input_profile["sets"]['t']['meas_points'] = []
                for set in input_profile["sets"].keys():
                    if set in input_data.columns.values.tolist():
                        input_profile["sets"][set]['meas_points'] = list({n: mani for n, mani in zip(range(1,n_exp+1), input_data[set].tolist())}.values())

                time_normalization_granularity = 3.235726/1

                input_profile["sets"]['t']['meas_points'] = [int(round(time/time_normalization_granularity,0)) for time in input_profile["sets"]['t']['meas_points']]

                input_profile["sets"]['t']['init_points'] = list(range(0,max(input_profile["sets"]['t']['meas_points'])+1))

                # Dummy; we use function here
                input_profile["manipulated_var"] = []
                for index, var in enumerate(manipulated_var):
                    var["value"] = {n: mani for n, mani in zip(range(1,n_exp+1), input_data[manipulated_var[index]["variable"]].tolist())}
                    input_profile["manipulated_var"].append(manipulated_var[index])

                # Dirac impulse function of tracer injection
                def input_function(node):
                    return (f"   def _inputfunc(m, t):\n" +
                            f"       if t == 0:\n" +
                            f"            return (m.{node.unique_representation}[t] == 0.035)\n" + # THIS IS NOW MASS AND DIVISION BY VOLUME IN OBJECT LIBRARY
                            f"       else:\n" +
                            f"            return (m.{node.unique_representation}[t] == 0)\n" +
                            f"   m.inputfunc = Constraint(m.t, rule=_inputfunc)\n"
                            )
                
                input_profile["input_function"] = input_function

                input_profile["measured_var"] = []
                for index, var in enumerate(measured_var):
                    var["value"] = {n: meas for n, meas in zip(input_profile["sets"]['t']['meas_points'], input_data[measured_var[index]["variable"]+"["+str(measured_var[index]["index"])+"]"].tolist())}
                    input_profile["measured_var"].append(measured_var[index])

                input_profile["n_exp"] = n_exp

                return input_profile

            if modus == "hierarchic_data":

                # Name and index of measured variable
                measured_var = [{"target":"envflow2","variable":"c_conv","index":3}, # product
                                {"target":"envflow2","variable":"c_conv","index":2}] # remaining educt

                manipulated_var = []

                n_exp = 1
                
                input_profile = {}
                input_profile["sets"] = {
                        'i':{'min': 1, 'max': 3, 'type': 'discrete', 'description': "components"},
                        "V_PFR":{'min': 0, 'max': 7.334, 'type': 'continuous', 'description': "volume for PFR"}
                        }
                
                input_profile["sets"]["V_PFR"]["meas_points"] = []
                
                input_profile["known_values"] = [
                                {"target":"envflow1", "variable":"V_dot_conv", "value":17/60},
                                {"target":"envflow1", "variable":"c_conv", "value":{1:0.10,2:0.10,3:0}},
                                # {"target":"ap_reaction", "variable":"k", "value":0.05746875}, #2nd order
                                # {"target":"ap_reaction", "variable":"k", "value":0.003375}, # 1st order
                                {"target":"ap_reaction", "variable":"E", "value":26470},
                                {"target":"ap_reaction", "variable":"Rg", "value":8.314},
                                {"target":"ap_reaction", "variable":"Tref", "value":293},
                                {"target":"ap_reaction", "variable":"nu_i", "value":{1:-1,2:-1,3:1}},
                                {"target":"ap_reaction", "variable":"ord_i_A1", "value":{1:1,2:1,3:0}},
                                {"target":"ap_reaction", "variable":"ord_i_A2", "value":{1:1,2:0,3:0}},
                                {"target":"ap_reaction", "variable":"ord_i_A3", "value":{1:1,2:2,3:0}},
                                {"target":"ap_reaction", "variable":"ord_i_A4", "value":{1:1,2:1,3:1}},
                                {"target":"environment", "variable":"T", "value":298},
                                {"target":"compartment16", "variable":"V", "value":0.87},
                                {"target":"compartment36", "variable":"V", "value":0.87},
                                {"target":"compartment13", "variable":"V", "value":0.87},
                                {"target":"compartment44", "variable":"V", "value":0.87},
                                {"target":"compartment33", "variable":"V", "value":0.87},
                                {"target":"compartment8", "variable":"V", "value":0.868},
                                {"target":"compartment22", "variable":"V", "value":0.868},
                                {"target":"compartment30", "variable":"V", "value":7.334},
                                {"target":"compartment1", "variable":"V", "value":1.455},
                                {"target":"compartment25", "variable":"V", "value":0.87},
                                {"target":"compartment19", "variable":"V", "value":0.87},
                                {"target":"compartment41", "variable":"V", "value":0.87},
                                # Specify SPLIT streams from RTD topology
                                {"target":"interface60", "variable":"V_dot_conv", "value":0.033*17/60},
                                {"target":"interface48", "variable":"V_dot_conv", "value":0.967*17/60},
                                {"target":"interface12", "variable":"V_dot_conv", "value":0},
                                {"target":"interface64", "variable":"V_dot_conv", "value":17/60},
                                {"target":"interface20", "variable":"V_dot_conv", "value":0},
                                {"target":"interface38", "variable":"V_dot_conv", "value":17/60},
                                {"target":"interface43", "variable":"V_dot_conv", "value":0},
                                {"target":"interface68", "variable":"V_dot_conv", "value":17/60},
                                ]

                input_data = pd.read_csv('./workflow/inputs/input_data_apreaction_half.csv', delimiter=";")

                # Dummy
                input_profile["manipulated_var"] = []
                for index, var in enumerate(manipulated_var):
                    var["value"] = {n: mani for n, mani in zip(range(1,n_exp+1), input_data[manipulated_var[index]["variable"]].tolist())}
                    input_profile["manipulated_var"].append(manipulated_var[index])

                input_profile["measured_var"] = []
                for index, var in enumerate(measured_var):
                    var["value"] = {n: meas for n, meas in zip(range(1,n_exp+1), input_data[measured_var[index]["variable"]+"["+str(measured_var[index]["index"])+"]"].tolist())}
                    input_profile["measured_var"].append(measured_var[index])

                input_profile["n_exp"] = n_exp

                return input_profile

    def initialize_topology(self, case_study, building_blocks, modus):

        topology = Topology(building_blocks)

        # We always have the environment building block
        if case_study == "insilico-ptc":
            environment = ENV_PTC("environment")
            environment.is_environment = True
        elif case_study == "rtd":
            environment = ENV("environment")
            environment.is_environment = True

        topology.add_compartment(environment)

        if case_study == "insilico-ptc":
            
            # For case study 1, there are two incoming/leaving streams, one for each phase
            new_interface = VALVE("interface" + str(topology.interface_counter), modus)
            new_interface.compartment_from = environment
            new_interface.connection_from_id = environment.connections[2]["id"]
            new_interface.compartment_to = environment
            new_interface.connection_to_id = environment.connections[0]["id"]
            new_interface.is_open = False
            new_interface.is_envflow_in = True
            new_interface.is_envflow_out = True
            environment.interfaces_in.append(new_interface)
            environment.interfaces_out.append(new_interface)
            topology.add_interface(new_interface)

            new_interface = VALVE("interface" + str(topology.interface_counter), modus)
            new_interface.compartment_from = environment
            new_interface.connection_from_id = environment.connections[3]["id"]
            new_interface.compartment_to = environment
            new_interface.connection_to_id = environment.connections[1]["id"]
            new_interface.is_open = False
            new_interface.is_envflow_in = True
            new_interface.is_envflow_out = True
            environment.interfaces_in.append(new_interface)
            environment.interfaces_out.append(new_interface)
            topology.add_interface(new_interface)

        if case_study == "tcr-rtd":
            
            # For case study 2, there is only the incoming tracer or the reactants
            new_interface = VALVE("interface" + str(topology.interface_counter), modus)
            new_interface.compartment_from = environment
            new_interface.connection_from_id = environment.connections[1]["id"]
            new_interface.compartment_to = environment
            new_interface.connection_to_id = environment.connections[0]["id"]
            new_interface.is_open = False
            new_interface.is_envflow_in = True
            new_interface.is_envflow_out = True
            environment.interfaces_in.append(new_interface)
            environment.interfaces_out.append(new_interface)
            topology.add_interface(new_interface)

        if case_study == "hierarchic_data":

            new_interface = VALVE("interface" + str(topology.interface_counter), modus)
            new_interface.compartment_from = environment
            new_interface.connection_from_id = environment.connections[1]["id"]
            new_interface.compartment_to = environment
            new_interface.connection_to_id = environment.connections[0]["id"]
            new_interface.is_open = False
            new_interface.is_envflow_in = True
            new_interface.is_envflow_out = True
            environment.interfaces_in.append(new_interface)
            environment.interfaces_out.append(new_interface)
            topology.add_interface(new_interface)

        # Postprocess initial topology (canonize etc.)
        topology.get_object_colors()
        topology.get_canon_labels()
        topology.get_canon_trace()
        topology.find_disconnecting_pairs()

        return topology
