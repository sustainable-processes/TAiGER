import json
import datetime

import pandas as pd
import numpy as np

from workflow import Workflow

# ToDo:
# Include noise
# Vary number of data points
# Measure computation time

# SETTINGS
workflow_modus = "modus-reduced-model-space-learning-curves"  # Choose from: "modus-normal" (not fully implemented), "modus-reduced-model-space", "modus-reduced-model-space-learning-curves", "modus-explore-reduced-model-space"
number_of_workflow_runs = 10                # Usually 1. When in "modus-reduced-model-space-learning-curves" commonly 50, 100, or 200.
episodes = 5                                # 100, number of models to generate, should be #oftrajectories if "modus-explore-reduced-model-space"
training_policy = "eps-greedy-static"       # Choose from: "eps-greedy-static", "eps-greedy-dynamic", "trainingpolicy-3" (not fully implemented), "trainingpolicy-4" (not fully implemented)
epsilon = 0.6                               # Choose between [0,1]. Low favors exploitation, high favors exploration. Only needed if trainings policy is "eps-greedy-static".     
max_epsilon = 1                             # Usually 1. Epsilon linearly decreases to 0 from the specified value. Only needed if trainings policy is "eps-greedy-dynamic".
reward_policy = "no-complexity-penalty"     # Choose from: "no-complexity-penalty", "with-complexity-penalty"
updating_policy = "averaging"               # Choose from: "averaging"
case_study = "cs-insilico"                  # Choose from: "cs-insilico", "cs-experimental"
data_size = "21-pts"                        # For "cs-insilico" choose from: "21-pts", For "cs-experimental" choose from: "7-pts"
noise = "no-noise"                          # For "cs-insilico" choose from: "no-noise", For "cs-experimental" choose from: -
save_result_dictionaries = True            # Might want to set to False when using "modus-reduced-model-space-learning-curves" since many models are tested (number_of_workflow_runs * episodes). Note that in order to save the result dictionary as json in folder "outputs", the Q-table should not be added to the results dictionary.


# RUN WORKFLOW
iterations_until_optimal_found = []   # If in modus "modus-reduced-model-space-learning-curves", this list records the number of iterations needed to first arrive at truth model (which is "trjectory 0"). The fewer iterations needed, the better the RL workflow works.
for run in range(number_of_workflow_runs):
    print("Number of workflow runs: " + str(run) + "/" + str(number_of_workflow_runs))
    
    workflow = Workflow()
    results_dict = workflow.run_workflow(workflow_modus,
                                         episodes, 
                                         training_policy, 
                                         epsilon, 
                                         max_epsilon, 
                                         reward_policy,
                                         updating_policy,
                                         case_study,
                                         data_size,
                                         noise)

    if save_result_dictionaries:
        print(results_dict)
        json_string = json.dumps(results_dict, indent=4)
        with open("./workflow/outputs/results_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json", "w") as json_file:
            json_file.write(json_string)
    
    if workflow_modus == "modus-reduced-model-space-learning-curves":
        iterations_until_optimal_found.append(len(results_dict)) # records number of iterations needed to first arrive at perfect/truth model


# If in modus "modus-reduced-model-space-learning-curves", the following code saves learning curves to a csv. To plot the learning curves, i.e., the csv, run ./workflow/plotting_scripts/plot_learning_curves.py.
if workflow_modus == "modus-reduced-model-space-learning-curves":
    df_iterations_until_optimal_found = pd.DataFrame({"Iterations_until_found": iterations_until_optimal_found})
    df_count = df_iterations_until_optimal_found["Iterations_until_found"].value_counts().reset_index() 
    df_count.columns = ["Iterations_until_found", "Count"]
    df_count = df_count.sort_values(by='Iterations_until_found').reset_index(drop=True) # e.g., [0 35, 3 2, ...] has been found in 1st iteration in 35 experiments, has never been found in 2nd iteration, two times in fourth iteration ...
    df_count = df_count[df_count["Iterations_until_found"] != episodes] # Filter out workflow runs where maximum number of episodes where achieved (since here the optimal model has not been found in time)
    df_count = df_count.append({'Iterations_until_found': episodes, 'Count': 0}, ignore_index=True) # Add for nicer curve in figure
    df_count["Count_cummulative_normalized"] = (100/number_of_workflow_runs) * np.cumsum(df_count["Count"])
    if training_policy == "eps-greedy-static":
        df_count.to_csv("./workflow/outputs/learning_curves/lc_" + "eps-" + str(epsilon) + "_" + reward_policy + "_" + data_size + "_" + noise + ".csv", index=False)
    elif training_policy == "eps-greedy-dynamic":
        df_count.to_csv("./workflow/outputs/learning_curves/lc_" + "eps-dyn" + "_" + reward_policy + "_" + data_size + "_" + noise + ".csv", index=False)
    #print(df_count)
