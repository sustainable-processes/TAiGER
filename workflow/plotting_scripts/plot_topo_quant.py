import matplotlib.pyplot as plt
import numpy as np
import pickle
import os
from tikzplotlib import save as tikz_save

# some_file.py
import sys
# caution: path[0] is reserved for script path (or '' in REPL)
sys.path.insert(1, './workflow/')

results_path = "./results_store/CS1/"

# CS1 ACC NEW
result_files = [
    # "QUANT_EPS_ACC_99_2024-08-07/QUANT_EPS2_ACC_99_2024-08-07_19-07-13",
    # "QUANT_EPS_ACC_99_2024-08-07/QUANT_EPS4_ACC_99_2024-08-07_19-08-27",
    # "QUANT_EPS_ACC_99_2024-08-07/QUANT_EPS6_ACC_99_2024-08-07_18-43-28",
    # "QUANT_EPS_ACC_99_2024-08-07/QUANT_EPS8_ACC_99_2024-08-07_18-45-32",
    "QUANT_EPS_ACC_99_2024-08-07/QUANT_EPS10_ACC_99_2024-08-07_18-33-55",

    # Better overall
    "QUANT_EPS_BN_99_2024-08-12/QUANT_EPS2_BN_99_2024-08-11_22-08-49",
    "QUANT_EPS_BN_99_2024-08-12/QUANT_EPS4_BN_99_2024-08-11_21-19-55",
    "QUANT_EPS_BN_99_2024-08-12/QUANT_EPS6_BN_99_2024-08-11_21-42-22",
    "QUANT_EPS_BN_99_2024-08-12/QUANT_EPS8_BN_99_2024-08-11_16-23-07",
    "QUANT_EPS_BN_99_2024-08-12/QUANT_EPS10_BN_99_2024-08-11_16-20-46",

    # High impact of learning
    # "QUANT_ALTLIB_2024-08-12/QUANT_EPS2_ALTLIB_99_2024-08-12_15-26-04",
    # "QUANT_ALTLIB_2024-08-12/QUANT_EPS4_ALTLIB_99_2024-08-12_16-12-51",
    # "QUANT_ALTLIB_2024-08-12/QUANT_EPS6_ALTLIB_99_2024-08-12_13-42-04",
    # "QUANT_ALTLIB_2024-08-12/QUANT_EPS8_ALTLIB_99_2024-08-12_15-42-51",
    # "QUANT_ALTLIB_2024-08-12/QUANT_EPS10_ALTLIB_99_2024-08-12_14-48-41",


    # "QUANT_MULTILEARN_2024-08-13/QUANT_EPS4_MULTILEARN_99_2024-08-12_22-47-10",
    # "QUANT_MULTILEARN_2024-08-13/QUANT_EPS6_MULTILEARN_99_2024-08-13_00-47-39",
    # "QUANT_MULTILEARN_2024-08-13/QUANT_EPS8_MULTILEARN_99_2024-08-12_22-26-07",

    # Much much much better (almost perfect reliable)
    # "QUANT_EPS_GGNOMIX_99_2024-08-08/QUANT_EPS2_GGNOMIX_99_2024-08-08_16-58-11",
    # "QUANT_EPS_GGNOMIX_99_2024-08-08/QUANT_EPS4_GGNOMIX_99_2024-08-08_16-19-03",
    # "QUANT_EPS_GGNOMIX_99_2024-08-08/QUANT_EPS6_GGNOMIX_99_2024-08-08_16-45-33",
    # "QUANT_EPS_GGNOMIX_99_2024-08-08/QUANT_EPS8_GGNOMIX_99_2024-08-08_16-00-27",
    # "QUANT_EPS_GGNOMIX_99_2024-08-08/QUANT_EPS10_GGNOMIX_99_2024-08-08_16-01-00",

    # Much worse in general
    # "QUANT_EPS_NOMIX_99_2024-08-08/QUANT_EPS2_NOMIX_99_2024-08-08_15-53-16",
    # "QUANT_EPS_NOMIX_99_2024-08-08/QUANT_EPS4_NOMIX_99_2024-08-08_15-50-21",
    # "QUANT_EPS_NOMIX_99_2024-08-08/QUANT_EPS6_NOMIX_99_2024-08-08_15-44-36",
    # "QUANT_EPS_NOMIX_99_2024-08-08/QUANT_EPS8_NOMIX_99_2024-08-08_15-47-26",
    # "QUANT_EPS_NOMIX_99_2024-08-08/QUANT_EPS10_NOMIX_99_2024-08-08_15-40-47",

    # Faster up until 1 min and more influence of learning
    # "QUANT_EPS_NOLOOP_99_2024-08-08/QUANT_EPS2_NOLOOP_99_2024-08-08_17-22-55",
    # "QUANT_EPS_NOLOOP_99_2024-08-08/QUANT_EPS4_NOLOOP_99_2024-08-08_16-47-59",
    # "QUANT_EPS_NOLOOP_99_2024-08-08/QUANT_EPS6_NOLOOP_99_2024-08-08_16-33-17",
    # "QUANT_EPS_NOLOOP_99_2024-08-08/QUANT_EPS8_NOLOOP_99_2024-08-08_16-46-22",
    # "QUANT_EPS_NOLOOP_99_2024-08-08/QUANT_EPS10_NOLOOP_99_2024-08-08_16-32-38",

    # Much better and more influence of learning
    # "QUANT_EPS_MUSTMT_99_2024-08-08/QUANT_EPS2_MUSTMT_99_2024-08-08_16-38-23",
    # "QUANT_EPS_MUSTMT_99_2024-08-08/QUANT_EPS4_MUSTMT_99_2024-08-08_16-22-50",
    # "QUANT_EPS_MUSTMT_99_2024-08-08/QUANT_EPS6_MUSTMT_99_2024-08-08_16-07-33",
    # "QUANT_EPS_MUSTMT_99_2024-08-08/QUANT_EPS8_MUSTMT_99_2024-08-08_16-01-32",
    # "QUANT_EPS_MUSTMT_99_2024-08-08/QUANT_EPS10_MUSTMT_99_2024-08-08_15-57-39",

    # Much faster in beginning, but not as good as NOLOOP or MUSTMT alone (interesting)
    # "QUANT_EPS_NOLOOP+MUSTMT_99_2024-08-08/QUANT_EPS2_NOLOOP+MUSTMT_99_2024-08-08_16-39-20",
    # "QUANT_EPS_NOLOOP+MUSTMT_99_2024-08-08/QUANT_EPS4_NOLOOP+MUSTMT_99_2024-08-08_16-01-20",
    # "QUANT_EPS_NOLOOP+MUSTMT_99_2024-08-08/QUANT_EPS6_NOLOOP+MUSTMT_99_2024-08-08_16-05-17",
    # "QUANT_EPS_NOLOOP+MUSTMT_99_2024-08-08/QUANT_EPS8_NOLOOP+MUSTMT_99_2024-08-08_16-06-00",
    # "QUANT_EPS_NOLOOP+MUSTMT_99_2024-08-08/QUANT_EPS10_NOLOOP+MUSTMT_99_2024-08-08_15-57-20",

    # Almost the same as pure ACC (interesting), role of learning relatively late relevant
    # "QUANT_EPS_NOLOOP+REACTION+MT+NOMIX_99_2024-08-08/QUANT_EPS2_NOLOOP+REACTION+MT+NOMIX_99_2024-08-08_17-33-56",
    # "QUANT_EPS_NOLOOP+REACTION+MT+NOMIX_99_2024-08-08/QUANT_EPS4_NOLOOP+REACTION+MT+NOMIX_99_2024-08-08_16-55-47",
    # "QUANT_EPS_NOLOOP+REACTION+MT+NOMIX_99_2024-08-08/QUANT_EPS6_NOLOOP+REACTION+MT+NOMIX_99_2024-08-08_16-54-06",
    # "QUANT_EPS_NOLOOP+REACTION+MT+NOMIX_99_2024-08-08/QUANT_EPS8_NOLOOP+REACTION+MT+NOMIX_99_2024-08-08_16-44-07",
    # "QUANT_EPS_NOLOOP+REACTION+MT+NOMIX_99_2024-08-08/QUANT_EPS10_NOLOOP+REACTION+MT+NOMIX_99_2024-08-08_16-58-41",


]

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
        if any(results_dicts[0][i][j]["accuracy_reward"] > 0.9999 for j in range(len(results_dicts[0][i]))):
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
                labels.append('run0 (' + results_filename + ')')


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
    plt.plot(times, numbered_labels, marker='o', ms=2, linestyle='-', label=labels[0].split(' (')[1][:-1])


# Set x-axis limits and ticks
max_time = max(time for times in all_times_per_file for time in times if time != 300)

# All x the same ca. 40 min
# max_time = 40
# plt.xlim(0, max_time * 1.05)

# Zoom X
# max_time = 10
plt.xlim(0, max_time * 1.04)

plt.xlabel('Time (min)')
plt.ylabel('Probability of Finding Truth Model')
plt.grid(True)

yticks = np.arange(0, 37, 2)
ytick_labels = [f'{2*(y)}%' for y in yticks]
plt.yticks(yticks, ytick_labels)

# Adding a legend for clarity
plt.legend()

plt.tight_layout()

# plt.show()

# Bug workaround
def tikzplotlib_fix_ncols(obj):
    """
    workaround for matplotlib 3.6 renamed legend's _ncol to _ncols, which breaks tikzplotlib
    """
    if hasattr(obj, "_ncols"):
        obj._ncol = obj._ncols
    for child in obj.get_children():
        tikzplotlib_fix_ncols(child)

tikzplotlib_fix_ncols(fig)

tikz_save("./workflow/plotting_scripts/plot.tex")
