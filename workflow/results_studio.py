import pickle
from jaal import Jaal
import matplotlib.pyplot as plt
from tikzplotlib import save as tikz_save

### This script is used to import result files and examine their contents
results_path = "./workflow/outputs/results/"
results_filename = "QUANT_EPS8_2024-07-31_18-13-41"

results_file = open(results_path + results_filename, 'rb')    
results_dict = pickle.load(results_file)
results_file.close()

print("Stop / debug here to inspect results")

#########################################################################

### Script to generate tally plot (see thesis Figure 4.7)

results_path = "./workflow/outputs/results/"
results_filename = "QUANT_GOODMODELS/QUANT_EPS10_GOODMODELS_2024-08-11_13-29-57"
e = 11
edge_noDups_df = results_dict[0][1][e]["jaal_info"][0]
node_df = results_dict[0][1][e]["jaal_info"][1]
Jaal(edge_noDups_df, node_df).plot(directed=True)

tally = {"[0,0.1)":0, "[0.1,0.2)":0, "[0.2,0.3)":0, "[0.3,0.4)":0, "[0.4,0.5)":0, "[0.5,0.6)":0, "[0.6,0.7)":0, "[0.7,0.8)":0, "[0.8,0.9)":0, "[0.9,0.99)":0, "[0.99,0.999999)":0, "[0.999999,1]":0}

for dict in results_dict[0]:
    for model in results_dict[0][dict]:
        if results_dict[0][dict][model]["accuracy_reward"] >= 0 and results_dict[0][dict][model]["accuracy_reward"] < 0.1:
            tally["[0,0.1)"] += 1
        if results_dict[0][dict][model]["accuracy_reward"] >= 0.1 and results_dict[0][dict][model]["accuracy_reward"] < 0.2:
            tally["[0.1,0.2)"] += 1
        if results_dict[0][dict][model]["accuracy_reward"] >= 0.2 and results_dict[0][dict][model]["accuracy_reward"] < 0.3:
            tally["[0.2,0.3)"] += 1
        if results_dict[0][dict][model]["accuracy_reward"] >= 0.3 and results_dict[0][dict][model]["accuracy_reward"] < 0.4:
            tally["[0.3,0.4)"] += 1
        if results_dict[0][dict][model]["accuracy_reward"] >= 0.4 and results_dict[0][dict][model]["accuracy_reward"] < 0.5:
            tally["[0.4,0.5)"] += 1
        if results_dict[0][dict][model]["accuracy_reward"] >= 0.5 and results_dict[0][dict][model]["accuracy_reward"] < 0.6:
            tally["[0.5,0.6)"] += 1
        if results_dict[0][dict][model]["accuracy_reward"] >= 0.6 and results_dict[0][dict][model]["accuracy_reward"] < 0.7:
            tally["[0.6,0.7)"] += 1
        if results_dict[0][dict][model]["accuracy_reward"] >= 0.7 and results_dict[0][dict][model]["accuracy_reward"] < 0.8:
            tally["[0.7,0.8)"] += 1
        if results_dict[0][dict][model]["accuracy_reward"] >= 0.8 and results_dict[0][dict][model]["accuracy_reward"] < 0.9:
            tally["[0.8,0.9)"] += 1
        if results_dict[0][dict][model]["accuracy_reward"] >= 0.9 and results_dict[0][dict][model]["accuracy_reward"] < 0.99:
            tally["[0.9,0.99)"] += 1
        if results_dict[0][dict][model]["accuracy_reward"] >= 0.99 and results_dict[0][dict][model]["accuracy_reward"] < 0.999999:
            tally["[0.99,0.999999)"] += 1
        if results_dict[0][dict][model]["accuracy_reward"] >= 0.999999 and results_dict[0][dict][model]["accuracy_reward"] <= 1:
            tally["[0.999999,1]"] += 1

sum_models = sum(tally[x] for x in tally)
tally = {k: v/sum_models*100 for k, v in tally.items()}

# Example dictionary
data = tally

# Extract keys and values
keys = list(data.keys())
values = list(data.values())

fig = plt.figure(figsize=(12, 6))

# Create the bar chart for all entries except the last four
plt.bar(keys[:-3], values[:-3], color=(31/255,119/255,180/255))

# Plot the last four entries as a single stacked bar
stacked_base = 0
labels = keys[-3:]
for i in range(3):
    plt.bar('[0.9,1]', values[-3 + i], bottom=stacked_base, color=[(148/255,103/255,189/255), (214/255,39/255,40/255), (44/255,160/255,44/255), (255/255,127/255,14/255)][i], label=labels[i])
    stacked_base += values[-3 + i]

# Add labels and title
plt.xlabel('Reward in Range')
plt.ylabel('"%" of Models')
plt.title('Procentual Number of Models in Different Accuracy Ranges, 448')
plt.legend()

# Display the chart
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

print()
