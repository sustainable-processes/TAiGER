# importing package
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#df_1 = pd.read_csv('./workflow/outputs/learning_curves/lc_eps-0.5_no-complexity-penalty_20-pts_no-noise.csv')
df_1 = pd.read_csv('./workflow/outputs/learning_curves/lc_eps-0.6_no-complexity-penalty_21-pts_no-noise.csv')

reference_line_y = [100,100]
reference_line_x = [0,100]

# plot lines (alpha = 0.1)
#plt.plot(duration_eps_03, count_eps_03, alpha = 0.1, linewidth=1, color = 'blue', label = "Change of mixing: 60rpm")

plt.plot(reference_line_x, reference_line_y, linewidth=1, linestyle='--', color = "black")
#plt.plot(duration_eps_01, count_eps_01, alpha = 0.3, linewidth=1, marker='+', color = "darkred", label = "eps = 0.1")
#plt.plot(duration_eps_03, count_eps_03, alpha = 0.3, linewidth=1, marker='+', color = "firebrick", label = "eps = 0.3")
plt.plot(df_1["Iterations_until_found"], df_1["Count_cummulative_normalized"], alpha = 1, linewidth=1, marker='+', color = "indianred", label = "eps = 0.5, no penalty")
#plt.plot(duration_eps_07, count_eps_07, alpha = 0.3, linewidth=1, marker='+', color = "lightcoral", label = "eps = 0.7")
#plt.plot(df_1["Iterations_until_found"], df_1["Count_cummulative_normalized"], alpha = 0.3, linewidth=1, marker='+', color = "rosybrown", label = "eps = 0.9")

#plt.plot(duration_eps_10, count_eps_10, alpha = 0.3, linewidth=1, marker='+', color = "forestgreen", label = "eps = 1")

#plt.plot(duration_dyn_eps, count_dyn_eps, linewidth=1, marker='+', color = 'darkgoldenrod', label = "dynamic eps")
#plt.plot(duration_eps_05_compl, count_eps_05_compl, linewidth=1, marker='+', color = 'darkblue', label = "eps = 0.5, w/ penalty")


plt.legend(loc='lower right', framealpha=0)
plt.xlabel("Iteration [-]")
plt.ylabel("Probability to find correct model [%]")
plt.show()



