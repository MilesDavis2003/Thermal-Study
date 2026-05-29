import pandas as pd
import matplotlib.pyplot as plt

filename = "Temp_Volt_time_data_Dual.csv"


def load_data(file):
    df = pd.read_csv(file)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def convert_time(df):
    """
    Converts timestamp into elapsed time in minutes from the start.
    """
    elapsed_sec = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds()
    elapsed_min = elapsed_sec / 60
    return elapsed_min


def plot_abs_temps(file):
    df = load_data(file)
    time_min = convert_time(df)

    plt.figure(figsize=(8, 5))

    plt.plot(time_min, df['temp_chmbr'], label = "Chamber Temp")
    plt.plot(time_min, df["tempP_0"], label="Chip 0 Absolute Temp")
    plt.plot(time_min, df["tempP_1"], label="Chip 1 Absolute Temp")

    plt.xlabel("Elapsed Time [min]")
    plt.ylabel("Absolute Temperature [°C]")
    plt.title("Absolute Temperature vs Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_rel_temps(file):
    df = load_data(file)
    time_min = convert_time(df)

    plt.figure(figsize=(8, 5))

    plt.plot(time_min, df["tempS_0"], label="Chip 0 Relative Temp")
    plt.plot(time_min, df["tempS_1"], label="Chip 1 Relative Temp")

    plt.xlabel("Elapsed Time [min]")
    plt.ylabel("Relative Temperature [°C]")
    plt.title("Relative Temperature vs Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# Call whichever one you want:
plot_abs_temps(filename)
plot_rel_temps(filename)