import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import re

from tikzplotlib import save as tikz_save

from matplotlib.lines import Line2D
from matplotlib.legend import Legend
Line2D._us_dashSeq    = property(lambda self: self._dash_pattern[1])
Line2D._us_dashOffset = property(lambda self: self._dash_pattern[0])
Legend._ncol = property(lambda self: self._ncols)

# Function to smooth the data using a rolling mean
def smooth_data(df, window_size=5):
    return df["concentration(g/L)"].rolling(window=window_size, min_periods=1).mean()

# Function to adjust concentration data by shifting the baseline to the last point
def shift_baseline(series):
    last_concentration = series.iloc[-1]
    return series - last_concentration

# Function to integrate concentration over time
def integrate_concentration(time, concentration):
    return np.trapz(concentration, time)

# Function to calculate the relative deviation from a reference value
def relative_deviation(product, reference_value=0.05):
    return abs((product - reference_value) / reference_value)

# Function to calculate the absolute deviation from a reference value
def absolute_deviation(product, reference_value=0.05):
    return abs(product - reference_value)

# Function to plot data for each RPM with three curves for each flow rate stacked vertically
def plot_by_rpm(csv_files, window_size=5):
    rpms = {}
    
    # Group files by RPM
    for file in csv_files:
        match = re.search(r'MB_MeCN_([\d.]+)ml_([\d.]+)rpm_rtd.csv', os.path.basename(file))
        if match:
            rpm = float(match.group(2))
            if rpm not in rpms:
                rpms[rpm] = []
            rpms[rpm].append(file)
    
    reference_value = 0.05
    
    # Create subplots for each RPM
    num_rpms = len(rpms)
    fig, axs = plt.subplots(num_rpms, 1, figsize=(10, 5 * num_rpms), sharex=True, sharey=True)
    fig.suptitle("Concentration vs Time for Different RPMs", fontsize=16)
    
    if num_rpms == 1:
        axs = [axs]  # Ensure axs is iterable if there is only one subplot
    
    for i, (rpm, files) in enumerate(rpms.items()):
        lines = []
        end_times = []
        start_times = []
        
        for file in files:
            df = pd.read_csv(file)
            
            # Debugging: Print column names
            print(f"Processing file: {file}")
            print("Columns:", df.columns)
            
            smoothed_concentration = smooth_data(df, window_size)
            adjusted_concentration = shift_baseline(smoothed_concentration)
            
            # Convert concentration from g/L to mg/L
            adjusted_concentration_mg = adjusted_concentration * 1000
            
            start_times.append(df["time/(min)"].iloc[0])
            end_times.append(df["time/(min)"].iloc[-1])
            
            # Extract flow rate and multiply by 2
            flow_rate = float(re.search(r'MB_MeCN_([\d.]+)ml_', os.path.basename(file)).group(1)) * 2
            
            # Plot in the corresponding subplot
            lines.append(axs[i].plot(df["time/(min)"], adjusted_concentration_mg, label=f"Flow Rate {flow_rate:.2f} ml")[0])
            axs[i].set_title(f"RPM {rpm:.2f}")
            axs[i].set_ylabel("Concentration (mg/L)")
            axs[i].grid(True)
        
        # Set x-axis limits to end at 12 minutes
        axs[i].set_xlim(0, 12)
        axs[i].set_ylim(-0.25,3.75)
        
        # Add single legend for each subplot
        axs[i].legend(loc="upper right")
    
    # Set x-axis label for the bottom subplot
    axs[-1].set_xlabel("Time (min)")
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    ## Bug workaround
    def tikzplotlib_fix_ncols(obj):
        """
        workaround for matplotlib 3.6 renamed legend's _ncol to _ncols, which breaks tikzplotlib
        """
        if hasattr(obj, "_ncols"):
            obj.f_ncol = obj._ncols
        for child in obj.get_children():
            tikzplotlib_fix_ncols(child)

    tikzplotlib_fix_ncols(fig)

    # tikz_save("./workflow/plotting_scripts/plot.tex")

    plt.show()

# List of csv files
path = "D:/Studium/Master/Master-Arbeit/jfal-msc-thesis/Experiments/TCR-RTD/MB_TCR_RTD/RTD_c_curve"
csv_files = [
    path + "/MB_MeCN_2.13ml_0rpm_rtd.csv",
    path + "/MB_MeCN_2.13ml_60rpm_rtd.csv",
    path + "/MB_MeCN_2.13ml_360rpm_rtd.csv",
    path + "/MB_MeCN_4.25ml_0rpm_rtd.csv",
    path + "/MB_MeCN_4.25ml_60rpm_rtd.csv",
    path + "/MB_MeCN_4.25ml_360rpm_rtd.csv",
    path + "/MB_MeCN_8.50ml_0rpm_rtd.csv",
    path + "/MB_MeCN_8.50ml_60rpm_rtd.csv",
    path + "/MB_MeCN_8.50ml_360rpm_rtd.csv"
]

# Choose the mode
mode = "by_rpm"  # Options: "all_in_one", "by_flow_rate", "by_rpm"

# Define the smoothing window size
window_size = 5

if mode == "by_rpm":
    plot_by_rpm(csv_files, window_size)
