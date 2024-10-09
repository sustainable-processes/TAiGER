from compartmentalization_workflow import Workflow
import datetime
import pickle
import sys

### This script is used to execute the workflow multiple times with different settings

def execute(num_config):

    num_runs = 50
    num_iter = 1
    case_study = "tcr-rtd"
    modus = "rtd"

    configurations = [
                    # {"name":"EPS2","data":"rtd","eps":0.2,"r_alloc":"AVERAGE","r_shape":"RTD_TEST","LL_multilearning":"off","LL_iter":1,"LL_eps":1},
                    # {"name":"EPS4","data":"rtd","eps":0.4,"r_alloc":"AVERAGE","r_shape":"RTD_TEST","LL_multilearning":"off","LL_iter":1,"LL_eps":1},
                    {"name":"EPS6","data":"rtd","eps":0.6,"r_alloc":"AVERAGE","r_shape":"RTD_TEST","LL_multilearning":"off","LL_iter":1,"LL_eps":1},
                    # {"name":"EPS8","data":"rtd","eps":0.8,"r_alloc":"AVERAGE","r_shape":"RTD_TEST","LL_multilearning":"off","LL_iter":1,"LL_eps":1},
                    # {"name":"EPS10","data":"rtd","eps":1,"r_alloc":"AVERAGE","r_shape":"RTD_TEST","LL_multilearning":"off","LL_iter":1,"LL_eps":1},
                    {"name":"EPS8_Q","data":"rtd","eps":0.8,"r_alloc":"AVERAGE","r_shape":"RTD_TEST","LL_multilearning":"off","LL_iter":1,"LL_eps":1, "Q_init":True},
    ]

    configurations = [configurations[num_config]]

    for config in configurations:

        if config["Q_init"]:
            Q_path = "./workflow/outputs/results/"
            Q_results_filename = "results_2024-08-06_14-18-47"

            Q_results_file = open(Q_path + Q_results_filename, 'rb')    
            Q_dict = pickle.load(Q_results_file)
            Q_results_file.close()
            Q = Q_dict["Q"]
        else:
            Q = 0

        result_dicts = {}
        durations = {}

        for i in range(0,num_runs):
            current_workflow = Workflow()
            result_dict, duration = current_workflow.run_workflow(num_iter, 
                                                                config["eps"], 
                                                                config["r_alloc"], 
                                                                config["r_shape"], 
                                                                config["LL_multilearning"], 
                                                                config["LL_iter"], 
                                                                config["LL_eps"], 
                                                                case_study, modus,
                                                                Q)
            result_dicts[i] = result_dict
            durations[i] = duration

        output = (result_dicts, durations)

        results_file = open('./workflow/outputs/results/QUANT_' + config["name"] + "_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), 'xb')
        pickle.dump(output, results_file)                    
        results_file.close() 

    print("Finished.")

if __name__ == "__main__":
    num_config = int(sys.argv[1])
    execute(num_config)