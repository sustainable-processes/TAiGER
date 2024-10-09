import matplotlib.pyplot as plt
import numpy as np
import pickle
import os
from tikzplotlib import save as tikz_save

# some_file.py
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, './workflow/')

results_path = "./results/TCR/"
result_files = [
    "QUANT_EPS6_OG_TRANS_2024-08-08_03-25-29",
    "QUANT_EPS6_Q_TRANS_2024-08-07_23-24-34",
]


# CS1 ACC NEW
# result_files = [
#     "QUANT_EPS_ACC_99_2024-08-07/QUANT_EPS2_ACC_99_2024-08-07_19-07-13",
#     "QUANT_EPS_ACC_99_2024-08-07/QUANT_EPS4_ACC_99_2024-08-07_19-08-27",
#     "QUANT_EPS_ACC_99_2024-08-07/QUANT_EPS6_ACC_99_2024-08-07_18-43-28",
#     "QUANT_EPS_ACC_99_2024-08-07/QUANT_EPS8_ACC_99_2024-08-07_18-45-32",
#     "QUANT_EPS_ACC_99_2024-08-07/QUANT_EPS10_ACC_99_2024-08-07_18-33-55",
# ]

# Initialize lists to hold data for each result file
all_times_per_file = []
all_labels_per_file = []

results_path = results_path

# Loop through each result file
for results_filename in result_files:
    results_dicts = {}
    results_file = open(os.path.join(results_path, results_filename), 'rb')
    results_dicts = pickle.load(results_file)
    results_file.close()

    found_good_model = {}
    time_to_terminate = {}
    iteration_to_terminate = {}

    # Extract data from the loaded result dictionaries
    for i in range(len(results_dicts[0])):
        # if any(results_dicts[0][i][j]["is_good"] for j in range(len(results_dicts[0][i]))):
        if any(results_dicts[0][i][j]["accuracy_reward"] > 0.85 for j in range(len(results_dicts[0][i])-1)):
            found_good_model["run" + str(i+1)] = True
        else:
            found_good_model["run" + str(i+1)] = False

        time_to_terminate["run" + str(i+1)] = results_dicts[1][i]

    # Initialize lists for this file
    times = []
    labels = []

    # Populate lists with data for this file
    for run, found in found_good_model.items():
        if found:
            times.append(time_to_terminate[run]/60)
            labels.append(run + ' (' + results_filename + ')')
        else:
            if not 300 in times:
                times.append(300)  # Large number representing "infinite"
                labels.append(run + ' (' + results_filename + ')')

    times.append(0)
    labels.append('run0 (QUANT_ZERO)')

    # Sort the times and labels based on times in ascending order
    sorted_indices = np.argsort(times)
    sorted_times = [times[i] for i in sorted_indices]
    sorted_labels = [labels[i] for i in sorted_indices]

    # Append to the overall lists
    all_times_per_file.append(sorted_times)
    all_labels_per_file.append(sorted_labels)

# Plotting
fig = plt.figure(figsize=(12, 6))

# Plot each set of data from different files
for times, labels in zip(all_times_per_file, all_labels_per_file):
    numbered_labels = [f'{2*(i)}%' for i in range(len(labels))]
    plt.plot(times, numbered_labels, marker='o', linestyle='-', label=labels[0].split(' (')[1][:-1])


# Set x-axis limits and ticks
max_time = max(time for times in all_times_per_file for time in times if time != 300)

# All x the same ca. 40 min
# max_time = 40
# plt.xlim(0, max_time * 1.05)

# Zoom X
# max_time = 5
plt.xlim(0, max_time * 1.04)

plt.xlabel('Time (min)')
plt.ylabel('Probability of Finding Good Model')
plt.grid(True)

yticks = np.arange(0, 51, 2)
ytick_labels = [f'{2*(y)}%' for y in yticks]
plt.yticks(yticks, ytick_labels)

# Adding a legend for clarity
plt.legend()

plt.tight_layout()

plt.show()

## Bug workaround
# def tikzplotlib_fix_ncols(obj):
#     """
#     workaround for matplotlib 3.6 renamed legend's _ncol to _ncols, which breaks tikzplotlib
#     """
#     if hasattr(obj, "_ncols"):
#         obj._ncol = obj._ncols
#     for child in obj.get_children():
#         tikzplotlib_fix_ncols(child)

# tikzplotlib_fix_ncols(fig)

# tikz_save("./workflow/plotting_scripts/plot.tex")
