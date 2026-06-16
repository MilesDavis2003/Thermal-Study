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
