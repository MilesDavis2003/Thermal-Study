# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.optimize import curve_fit
# import os

# def func(x, A, alpha):
#     return A*(1 - np.exp(-alpha * x))

# loc = 'Temp_Power_Data'
# files = os.listdir(loc)

# for fname in files:
#     print(f"Processing: {fname}")

#     df = pd.read_csv(loc + '/' + fname)
#     temp_abs = np.array(df['temp_abs'], dtype=float)
#     temp_rel = np.array(df['temp_rel'], dtype=float)
#     time = np.array(df['timestamp'], dtype=str)

#     t0 = 60 * float(time[0].split(':')[1]) + float(time[0].split(':')[2])
#     t_new = []
#     temp_abs_new = []
#     temp_rel_new = []

#     for count, t in enumerate(time):
#         mins = float(t.split(':')[1])
#         secs = float(t.split(':')[2])
#         t_total = 60 * mins + secs - t0
#         t_new.append(t_total)

#     t_new = np.array(t_new)

#     mask = t_new >= 0

#     opt, cov = curve_fit(func, t_new, temp_abs)
#     A_, alpha_ = opt
#     x = np.linspace(0, max(t_new), 1000)

#     t_new = t_new[mask]
#     temp_abs = temp_abs[mask]
#     plt.scatter(t_new, temp_abs)
#     plt.plot(x, func(x, A_, alpha_))
#     plt.grid(True)
# plt.show()


# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.optimize import curve_fit
# import os

# def func(x, A, alpha):
#     return A*(22.0 - np.exp(-alpha * x))

# loc = 'Temp_Power_Data'
# # loc = 'Dual_Chip_Temp_Data'
# files = os.listdir(loc)
# power = []
# tot_temp_abs = []

# def get_power(fname):
#     # Arduino_Data_46.3mW.csv -> 46.3
#     part = fname.split("_")[2]          # '46.3mW.csv'
#     power = part.replace("mW.csv", "")  # '46.3'
#     return float(power)

# files = sorted(files, key=get_power)

# for i, fname in enumerate(files):
#     print(f"Processing: {fname}")
#     f_split = fname.split('_')
#     pwr = f_split[2].replace('mW.csv', '')
#     power.append(pwr)

#     df = pd.read_csv(loc + '/' + fname)

#     temp_abs_0 = np.array(df['temp_abs_0'], dtype=float)
#     time = np.array(df['timestamp'], dtype=str)

#     # convert timestamps into seconds relative to first point
#     t0 = 60 * float(time[0].split(':')[1]) + float(time[0].split(':')[2])
#     t_new = []
#     temp_abs_new = []
#     temp_rel_new = []

#     for count, t in enumerate(time):
#         mins = float(t.split(':')[1])
#         secs = float(t.split(':')[2])
#         t_total = 60 * mins + secs - t0
#         t_new.append(t_total)

#     t_new = np.array(t_new)

#     mask = t_new >= 0

#     t_new = t_new[mask]
#     temp_abs_0 = temp_abs_0[mask]
#     # temp_rel = temp_rel[mask]

#     opt, cov = curve_fit(func, t_new, temp_abs_0)
#     A_, alpha_ = opt
#     tot_temp_abs.append(A_)
#     x = np.linspace(min(t_new), max(t_new), 1000)

#     plt.plot(x, func(x, A_, alpha_), label = f'{pwr} mW, {round(A_, 1)} C' )
#     plt.scatter(t_new, temp_abs)
#     plt.title('Temp vs Time')
#     plt.xlabel('Time [s]')
#     # plt.xlim(0, 150)
#     plt.ylabel('Abs Temp [C]')
#     plt.grid(True)
#     plt.legend()

# # # plt.tight_layout()
# plt.show()

# plt.plot(power, tot_temp_abs, marker = 'o')
# plt.title('Temp vs Power')
# plt.xlabel('Power [mW]')
# plt.ylabel('Abs Temp [C]')
# plt.grid()
# plt.show()



import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Settings
# -----------------------------
loc = "Dual_Chip_Temp_Data" # Change this
outdir = "Temp_Plots" # Change this
os.makedirs(outdir, exist_ok=True)

chip_colors = {
    0: "blue",
    1: "orange"
}

markers = ["o", "s", "^", "D", "v", "P", "X", "*", "<", ">"]

# -----------------------------
# Helper functions
# -----------------------------
def get_power(fname):
    # Example: Arduino_Data_46.3mW.csv
    match = re.search(r"([\d.]+)\s*mW", fname)
    if match is None:
        raise ValueError(f"Could not find power in filename: {fname}")
    return float(match.group(1))

def load_csv(path):
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()

    for col in ["temp_abs_0", "temp_rel_0", "temp_abs_1", "temp_rel_1"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["time_s"] = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds()

    df = df.dropna()
    return df

# -----------------------------
# Load files
# -----------------------------
files = [f for f in os.listdir(loc) if f.endswith(".csv")]
files = sorted(files, key=get_power)

final_results = []

# =========================================================
# Plot 1: Absolute temperature vs time
# =========================================================
plt.figure(figsize=(10, 6))

for i, fname in enumerate(files):
    power = get_power(fname)
    marker = markers[i % len(markers)]

    df = load_csv(os.path.join(loc, fname))

    for chip in [0, 1]:
        plt.scatter(
            df["time_s"],
            df[f"temp_abs_{chip}"],
            color=chip_colors[chip],
            marker=marker,
            s=25,
            alpha=0.75,
            label=f"Chip {chip}, {power} mW"
        )

        final_results.append({
            "power_mW": power,
            "chip": chip,
            "final_abs_temp": df[f"temp_abs_{chip}"].iloc[-1],
            "final_rel_temp": df[f"temp_rel_{chip}"].iloc[-1]
        })

plt.title("Absolute Temperature vs Time")
plt.xlabel("Time [s]")
plt.ylabel("Absolute Temperature [C]")
plt.grid(True)
plt.legend(fontsize=8, ncols=2)
plt.tight_layout()
plt.savefig(os.path.join(outdir, "abs_temp_vs_time_all_powers.png"), dpi=300)
plt.show()

# =========================================================
# Plot 2: Relative temperature vs time
# =========================================================
plt.figure(figsize=(10, 6))

for i, fname in enumerate(files):
    power = get_power(fname)
    marker = markers[i % len(markers)]

    df = load_csv(os.path.join(loc, fname))

    for chip in [0, 1]:
        plt.scatter(
            df["time_s"],
            df[f"temp_rel_{chip}"],
            color=chip_colors[chip],
            marker=marker,
            s=25,
            alpha=0.75,
            label=f"Chip {chip}, {power} mW"
        )

plt.title("Relative Temperature vs Time")
plt.xlabel("Time [s]")
plt.ylabel("Relative Temperature [C]")
plt.grid(True)
plt.legend(fontsize=8, ncols=2)
plt.tight_layout()
plt.savefig(os.path.join(outdir, "rel_temp_vs_time_all_powers.png"), dpi=300)
plt.show()

# =========================================================
# Plot 3: Final temperature vs power
# =========================================================
res = pd.DataFrame(final_results)

plt.figure(figsize=(8, 5))

for chip in [0, 1]:
    r = res[res["chip"] == chip]

    plt.scatter(
        r["power_mW"],
        r["final_abs_temp"],
        color=chip_colors[chip],
        marker="o",
        s=70,
        label=f"Chip {chip} abs final temp"
    )

    plt.plot(
        r["power_mW"],
        r["final_abs_temp"],
        color=chip_colors[chip],
        linewidth=2
    )

plt.title("Final Absolute Temperature vs Power")
plt.xlabel("Power [mW]")
plt.ylabel("Final Absolute Temperature [C]")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(outdir, "final_abs_temp_vs_power.png"), dpi=300)
plt.show()
