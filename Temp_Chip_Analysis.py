import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import numpy as np
import pandas as pd
import os

chip_0_data = "Temp_Chip_Data_0"
chip_1_data = "Temp_Chip_Data_1"
chip_2_data = "Temp_Chip_Data_2"
chip_3_data = "Temp_Chip_Data_3"

chip_01_data = "Temp_Chip_Data_01"

# Fit with A*(1 - e^{-x/t})
def fitting(x, A, tau):
    return A * (1 - np.exp(-x/tau))

# Sorting files from least to greatest power
def sort_by_power(names):
    def get_power(name):
        part = name.split("_")[2]   # gets something like "100mW"
        part0 = part.split(".")[0]
        return float(part0.replace("mW", ""))

    return sorted(names, key=get_power)

# Filter out baseline time
def filtering(x, y):
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)

    if len(x) != len(y):
        print("ERROR: Length of x data doesn't equal length of y data.")
        return None, None

    # Keep only points where y is positive
    mask = y > 0

    x_data = x[mask]
    y_data = y[mask]

    # If no positive y values exist
    if len(x_data) == 0:
        print("ERROR: No positive y values found.")
        return None, None

    # Shift x so first positive point starts at x = 0
    x_data = x_data - x_data[0]

    return x_data, y_data

# Turn timestamp format into seconds format
def time_format(timestamp):
    time0 = []
    time = []
    time_lst = np.array(timestamp, dtype=str)
    for i in time_lst:
        format = i.split('T')[1]
        t = float(format.split(':')[1]) * 60.0 + float(format.split(':')[2])
        time0.append(t)
    mini = min(time0)
    time = [round(j - mini, 2) for j in time0]
    return time

# Plot Chip 0 (First Chip from the 80 pin connector)
def plot_chip_0(chip_0):
    files = os.listdir(chip_0)
    chip_0_files = sort_by_power(files)

    info = []
    for fil in chip_0_files:
        power = str(fil.split("_")[2])
        df = pd.read_csv(chip_0 + '/' + fil)

        # This Changes when chip changes
        temp_abs = df['temp_abs_0']
        temp_abs = [j - temp_abs[0]-0.25 for j in temp_abs]
        timestamp = df['timestamp']
        time = time_format(timestamp)

        time_x, temp_y = filtering(time, temp_abs)

        p0 = [max(temp_y), 20]
        x = np.linspace(0, 500, 10000)
        opt, cov = curve_fit(fitting, time_x, temp_y, p0=p0)
        A, tau = opt
        
        info.append({
            'power': power,
            'tau': tau,
            'temp': A
        })

        # plt.plot(x, fitting(x, A, tau))

        plt.title('Chip 1 Temp Profile for Prototype Stave')
        # plt.plot(time_x, temp_y, label = f'{power}, \u03c4 = {round(tau, 1)}, Temp = {round(A, 1)}')
        plt.plot(time_x, temp_y, label = power)
        plt.xlabel('Time [sec]')
        plt.ylabel('Temp [C]')
        plt.xlim(0, 150)
        plt.grid(True)
        plt.legend()

    plt.show()
    return info

# Plot Chip 1 (Second Chip from the 80 pin connector)
def plot_chip_1(chip_1):
    files = os.listdir(chip_1)
    chip_1_files = sort_by_power(files)

    info = []
    for fil in chip_1_files:
        power = str(fil.split("_")[2])
        df = pd.read_csv(chip_1 + '/' + fil)

        # This Changes when chip changes
        temp_abs = df['temp_abs_1']
        temp_abs = [j - temp_abs[0]-0.25 for j in temp_abs]
        timestamp = df['timestamp']
        time = time_format(timestamp)

        time_x, temp_y = filtering(time, temp_abs)

        p0 = [max(temp_y), 20]
        x = np.linspace(0, 500, 10000)
        opt, cov = curve_fit(fitting, time_x, temp_y, p0=p0)
        A, tau = opt

        info.append({
            'power': power,
            'tau': tau,
            'temp': A
        })

        # plt.plot(x, fitting(x, A, tau))

        plt.title('Chip 2 Temp Profile for Prototype Stave')
        # plt.plot(time_x, temp_y, label = f'{power}, \u03c4 = {round(tau, 1)}, Temp = {round(A, 1)}')
        plt.plot(time_x, temp_y, label = power)
        plt.xlabel('Time [sec]')
        plt.ylabel('Temp [C]')
        plt.xlim(0, 150)
        plt.grid(True)
        plt.legend()

    plt.show()
    return info

def plot_tau_temp():
    chip_0 = plot_chip_0(chip_0_data)
    chip_1 = plot_chip_1(chip_1_data)

    chip_0_power = [d["power"] for d in chip_0]
    chip_0_temp  = [d["temp"]  for d in chip_0]
    chip_0_tau   = [d["tau"]   for d in chip_0]

    chip_1_power = [d["power"] for d in chip_1]
    chip_1_temp  = [d["temp"]  for d in chip_1]
    chip_1_tau   = [d["tau"]   for d in chip_1]

    fig, axs = plt.subplots(2, 2, figsize=(10, 6))

    plots = [
        (axs[0, 0], chip_0_power, chip_0_temp, "Chip 1 Temp vs Power", "Temp [C]"),
        (axs[0, 1], chip_1_power, chip_1_temp, "Chip 2 Temp vs Power", "Temp [C]"),
        (axs[1, 0], chip_0_power, chip_0_tau,  "Chip 1 Tau vs Power",  "Tau [s]"),
        (axs[1, 1], chip_1_power, chip_1_tau,  "Chip 2 Tau vs Power",  "Tau [s]"),
    ]

    for ax, power, values, title, ylabel in plots:
        ax.plot(power, values, marker="o")
        ax.set_title(title)
        ax.set_xlabel("Power [mW]")
        ax.set_ylabel(ylabel)
        ax.grid(True)

    plt.tight_layout()
    plt.show()

# def plot_chip_folder(folder):
#     files = [
#         f for f in os.listdir(folder)
#         if f.endswith(".csv") and "mW" in f
#     ]

#     # sort by power number in filename
#     files = sorted(
#         files,
#         key=lambda f: float(f.split("_")[-1].replace("mW.csv", ""))
#     )

#     fig_abs, ax_abs = plt.subplots(figsize=(10, 6))
#     fig_rel, ax_rel = plt.subplots(figsize=(10, 6))

#     for file in files:
#         path = os.path.join(folder, file)

#         power = file.split("_")[-1].replace(".csv", "")

#         df = pd.read_csv(path)

#         # remove spaces from column names just in case
#         df.columns = df.columns.str.strip()

#         t = pd.to_datetime(df["timestamp"])
#         time = (t - t.iloc[0]).dt.total_seconds()

#         # absolute temperature plot
#         ax_abs.plot(time, df["temp_abs_0"], label=f"Chip 0 {power}")
#         ax_abs.plot(time, df["temp_abs_1"], "--", label=f"Chip 1 {power}")

#         # relative temperature plot
#         ax_rel.plot(time, df["temp_rel_0"], label=f"Chip 0 {power}")
#         ax_rel.plot(time, df["temp_rel_1"], "--", label=f"Chip 1 {power}")

#     ax_abs.set_title("Absolute Temperature vs Time")
#     ax_abs.set_xlabel("Time [s]")
#     ax_abs.set_ylabel("Temperature [C]")
#     ax_abs.grid(True)
#     ax_abs.legend()

#     ax_rel.set_title("Relative Temperature vs Time")
#     ax_rel.set_xlabel("Time [s]")
#     ax_rel.set_ylabel("Relative Temperature [C]")
#     ax_rel.grid(True)
#     ax_rel.legend()

#     fig_abs.tight_layout()
#     fig_rel.tight_layout()

#     plt.show()


def clean_extreme_changes(time, y, max_change=5):
    """
    Removes points where y changes by more than max_change
    from the previous point.
    """
    time_clean = [time[0]]
    y_clean = [y[0]]

    for i in range(1, len(y)):
        if abs(y[i] - y_clean[-1]) <= max_change:
            time_clean.append(time[i])
            y_clean.append(y[i])

    return time_clean, y_clean


def plot_chip_folder(folder):
    files = [
        f for f in os.listdir(folder)
        if f.endswith(".csv") and "mW" in f
    ]

    files = sorted(
        files,
        key=lambda f: float(f.split("_")[-1].replace("mW.csv", ""))
    )

    fig_abs, ax_abs = plt.subplots(figsize=(10, 6))
    fig_rel, ax_rel = plt.subplots(figsize=(10, 6))

    for file in files:
        path = os.path.join(folder, file)
        power = file.split("_")[-1].replace(".csv", "")

        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()

        t = pd.to_datetime(df["timestamp"])
        time = (t - t.iloc[0]).dt.total_seconds()

        # only keep data up to 150 seconds
        mask = time <= 150
        time = time[mask].to_numpy()

        temp_abs_0 = df["temp_abs_0"][mask].to_numpy()
        temp_abs_1 = df["temp_abs_1"][mask].to_numpy()
        temp_rel_0 = df["temp_rel_0"][mask].to_numpy()
        temp_rel_1 = df["temp_rel_1"][mask].to_numpy()

        # clean sudden extreme dips/jumps
        t0, abs0 = clean_extreme_changes(time, temp_abs_0, max_change=5)
        t1, abs1 = clean_extreme_changes(time, temp_abs_1, max_change=5)
        t2, rel0 = clean_extreme_changes(time, temp_rel_0, max_change=5)
        t3, rel1 = clean_extreme_changes(time, temp_rel_1, max_change=5)

        ax_abs.plot(t0, abs0, label=f"Chip 1 {power}")
        ax_abs.plot(t1, abs1, "--", label=f"Chip 2 {power}")

        ax_rel.plot(t2, rel0, label=f"Chip 1 {power}")
        ax_rel.plot(t3, rel1, "--", label=f"Chip 2 {power}")

    ax_abs.set_title("Chip 1 & 2 Absolute Temperature vs Time")
    ax_abs.set_xlabel("Time [s]")
    ax_abs.set_ylabel("Temperature [C]")
    ax_abs.set_xlim(0, 150)
    ax_abs.grid(True)
    ax_abs.legend()

    ax_rel.set_title("Chip 1 & 2 Relative Temperature vs Time")
    ax_rel.set_xlabel("Time [s]")
    ax_rel.set_ylabel("Relative Temperature [C]")
    ax_rel.set_xlim(0, 150)
    ax_rel.grid(True)
    ax_rel.legend()

    fig_abs.tight_layout()
    fig_rel.tight_layout()

    plt.show()

plot_chip_folder(chip_01_data)
# plot_tau_temp()
# print(plot_chip_0(chip_0_data))
# plot_chip_1(chip_1_data)