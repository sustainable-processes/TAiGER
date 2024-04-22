import pandas as pd
import json

class InputModule():

    def generate_input_profile(self, case_study, data_size, noise) -> dict:

        if case_study == "cs-insilico":
            # ToDo: For thesis synthetic case study double check that these are realistic values. Might make parameter estimation of D_z possible.
            input_profile = {
                'sets': {'t':{'min': 0, 'max': 3600, 'type': 'continuous', 'description': "discretization in time"},
                         'z':{'min': 0, 'max': 0.1, 'type': 'continuous', 'description': "discretization along z-axis"},
                         'i':{'min': 1, 'max': 3, 'type': 'discrete', 'description': "indexes components"}, 
                         'p':{'min': 1, 'max': 1, 'type': 'discrete', 'description': "indexes reactions"},},    
                'c_i0': {1: 1, 2: 1, 3: 0},
                'v_z': 0.001,
                'd_j_i_dz': 0.1, # starting value for when this is chosen as to-be-fitted parameter and not variable
                'k_p': 0.1, # for when is parameter not variable
                'r_i': 0.1, # for when is parameter not variable
                'r_p': 0.1, # for when is parameter not variable
                'k_ref_p': {1: 0.1}, # mutable, true value (i.e. value used to generate data): 0.1
                'E_p': {1: 100}, # mutable, true value (i.e. value used to generate data): 100
                'R': 8.314,
                'T': 298,
                'T_ref': 300,
                'nu_ip': {(1,1): -1, (2,1): -2, (3,1): 1}, # Optional: add "default=0" to parameter options and only specify non-zero entries here.
                'ord_ip_1': {(1,1): 1, (2,1): 1, (3,1): 0}, # True: 1 1 0
                'ord_ip_2': {(1,1): 1, (2,1): 0, (3,1): 0}, # True: 1 1 0
                'ord_ip_3': {(1,1): 1, (2,1): 2, (3,1): 0}, # True: 1 1 0
                'ord_ip_4': {(1,1): 1, (2,1): 1, (3,1): 1}, # True: 1 1 0
                'D_z': 1e-5,  # mutable, true value (i.e. value used to generate data): 1e-5
            }

            

            if data_size == "21-pts" and noise == "no-noise":
                input_data = pd.read_csv('./workflow/inputs/input_data_insilico_21-pts_no-noise.csv')
        
        elif case_study == "cs-experimental":
            # ToDo: For thesis synthetic case study double check that these are realistic values. Might make parameter estimation of D_z possible.
            input_profile = {
                'sets': {'t': {'min': 0, 'max': 3600, 'type': 'continuous', 'description': "discretization in time"},
                         'z': {'min': 0, 'max': 0.182352, 'type': 'continuous', 'description': "discretization along z-axis"},
                         'i': {'min': 1, 'max': 3, 'type': 'discrete', 'description': "indexes components"},
                         'p': {'min': 1, 'max': 1, 'type': 'discrete', 'description': "indexes reactions"},},
                'c_i0': {1: 20, 2: 20, 3: 0}, # [mol/m3]
                'v_z': 0.003349, #[m/s]
                'd_j_i_dz': 0.1, # for when is parameter not variable
                'k_p': 0.024, # for when is parameter not variable
                'r_i': 0.1, # for when is parameter not variable
                'r_p': 0.1, # for when is parameter not variable
                'k_ref_p': {1: 0.02}, # mutable, true value (i.e. value used to generate data): 0.1
                'E_p': {1: 26470}, # mutable, true value (i.e. value used to generate data): 100
                'R': 8.314, # [J/mol/K]
                'T': 298, # [K]
                'T_ref': 293,  # [K]
                'nu_ip': {(1,1): -1, (2,1): -1, (3,1): 1}, # Optional: add "default=0" to parameter options and only specify non-zero entries here.
                'ord_ip_1': {(1,1): 1, (2,1): 1, (3,1): 0}, # True: 1 1 0
                'ord_ip_2': {(1,1): 1, (2,1): 0, (3,1): 0}, # True: 1 1 0
                'ord_ip_3': {(1,1): 1, (2,1): 2, (3,1): 0}, # True: 1 1 0
                'ord_ip_4': {(1,1): 1, (2,1): 1, (3,1): 1}, # True: 1 1 0
                'D_z': 2.14e-5,  # mutable, true value (i.e. value used to generate data): 1e-5, 1e-2 works, 2.14e-5 expected
            }

            if data_size == "7-pts" and noise == "no-noise":
                input_data = pd.read_csv('./workflow/inputs/input_data_experimental_7-pts_no-noise.csv')

        input_profile["c3_meas"] = {z: c3 for z, c3 in zip(input_data["z_[m]"].tolist(), input_data["c_product_[mol/m3]"].tolist())}


        return input_profile
