from compartmentalization_workflow import Workflow
from equation_workflow import run_from_init_topo

# SETTINGS
episodes = 1                               # Upper-level (topology generation) episodes
epsilon = 0.6                               # Upper-level exploitation vs. exploration (1 = only random exploration)
r_alloc = "AVERAGE"                         # Reward allocation over episode. "AVERAGE" or "BEST" (see thesis Page 40 & Figure 4.15)
r_shape = "ACC"                             # Reward shaping. "ACC" = No shaping beyond model accuracy
LL_episodes = 1                            # Lower-level (equation generation) episodes
LL_epsilon = 0.6                            # Lower-level exploitation vs. exploration (1 = only random exploration)
LL_multilearning = "OFF"                    # Integrate Q-tables over all lower-level episodes (NOT SAFE)

case_study = "insilico-ptc"                      # Choose from: "insilico-ptc", "tcr-rtd"
workflow_modus = "normal"                      # For RTD case study: "normal" (case study 1, topology+equation generation from same data), "rtd" (case study 2, fit topology to rtd data), "hierarchic_data" (case study 2, include reaction data in existing topology)

Q = 0                                       # See quant_studio for transfer learning

# RUN WORKFLOW
if workflow_modus == "normal" or workflow_modus == "rtd":
    workflow = Workflow()
    result_dict, duration = workflow.run_workflow(episodes,
                                                    epsilon,
                                                    r_alloc,
                                                    r_shape,
                                                    LL_multilearning,
                                                    LL_episodes,
                                                    LL_epsilon,
                                                    case_study, workflow_modus, Q)
    
elif workflow_modus == "hierarchic_data":
    run_from_init_topo()