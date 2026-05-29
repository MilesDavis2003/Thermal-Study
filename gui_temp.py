
# import tkinter as tk
# from tkinter import ttk
# import serial
# import threading
# import time
# from collections import deque

# from matplotlib.figure import Figure
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# PORT = "COM5"       # change this
# BAUD_RATE = 9600
# MAX_POINTS = 100

# class TemperatureMonitor:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Temperature Monitor")

#         self.running = True
#         self.ser = None

#         self.times = deque(maxlen=MAX_POINTS)
#         self.abs_temps = deque(maxlen=MAX_POINTS)
#         self.start_time = time.time()

#         self.abs_label = ttk.Label(root, text="Absolute Temp: --", font=("Arial", 14))
#         self.abs_label.pack(pady=5)

#         self.rel_label = ttk.Label(root, text="Relative Temp: --", font=("Arial", 14))
#         self.rel_label.pack(pady=5)

#         self.status_label = ttk.Label(root, text="Connecting...")
#         self.status_label.pack(pady=5)

#         self.fig = Figure(figsize=(7, 4), dpi=100)
#         self.ax = self.fig.add_subplot(111)
#         self.ax.grid(True)
#         self.ax.set_ylim(0, 50)
#         self.ax.set_title("Relative Temperature vs Time")
#         self.ax.set_xlabel("Time (s)")
#         self.ax.set_ylabel("Relative Temperature")

#         self.line, = self.ax.plot([], [])

#         self.canvas = FigureCanvasTkAgg(self.fig, master=root)
#         self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

#         try:
#             self.ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
#             self.status_label.config(text=f"Connected to {PORT} at {BAUD_RATE} baud")
#         except Exception as e:
#             self.status_label.config(text=f"Connection failed: {e}")
#             self.ser = None

#         if self.ser is not None:
#             self.thread = threading.Thread(target=self.read_serial, daemon=True)
#             self.thread.start()

#         self.update_plot()
#         self.root.protocol("WM_DELETE_WINDOW", self.close)

#     def read_serial(self):
#         while self.running and self.ser:
#             try:
#                 if self.ser.in_waiting > 0:
#                     line = self.ser.readline().decode("utf-8", errors="ignore").strip()

#                     if line:
#                         parts = line.split(",")

#                         if len(parts) == 2:
#                             abs_temp = float(parts[0].strip())
#                             rel_temp = float(parts[1].strip())

#                             current_time = time.time() - self.start_time

#                             self.times.append(current_time)
#                             self.abs_temps.append(abs_temp)

#                             self.root.after(0, self.update_labels, abs_temp, rel_temp)

#             except ValueError:
#                 pass
#             except Exception as e:
#                 self.root.after(0, lambda: self.status_label.config(text=f"Serial error: {e}"))
#                 break

#     def update_labels(self, abs_temp, rel_temp):
#         self.abs_label.config(text=f"Absolute Temp: {abs_temp:.2f}")
#         self.rel_label.config(text=f"Relative Temp: {rel_temp:.2f}")

#     def update_plot(self):
#         if len(self.times) > 0:
#             self.line.set_data(list(self.times), list(self.abs_temps))
#             self.ax.relim()
#             self.ax.autoscale_view()
#             self.canvas.draw()

#         if self.running:
#             self.root.after(500, self.update_plot)

#     def close(self):
#         self.running = False
#         if self.ser and self.ser.is_open:
#             self.ser.close()
#         self.root.destroy()

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TemperatureMonitor(root)
#     root.mainloop()







import re
import time
import serial
import tkinter as tk
from collections import deque

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# =============================
# Settings
# =============================
MAX_CHIPS = 4
WINDOW_SECONDS = 60

# Set True if you want to type chip numbers as 1,2,3,4
# Serial still uses temp_abs_0 ... temp_abs_3 internally.
ONE_BASED_INPUT = True


# =============================
# Helpers
# =============================
def parse_serial_line(line):
    """
    Arduino sends only values in order, for example:

    23.4,0.2,24.1,0.9,22.8,-0.4,25.0,1.8

    Meaning:
    temp_abs_0, temp_rel_0,
    temp_abs_1, temp_rel_1,
    temp_abs_2, temp_rel_2,
    temp_abs_3, temp_rel_3
    """

    values = [float(x.strip()) for x in line.split(",") if x.strip() != ""]

    data = {}

    for chip in range(MAX_CHIPS):
        abs_index = 2 * chip
        rel_index = 2 * chip + 1

        if rel_index < len(values):
            data[f"temp_abs_{chip}"] = values[abs_index]
            data[f"temp_rel_{chip}"] = values[rel_index]

    return data

def parse_chip_input(text):
    """
    Example input:
    1,4  -> chips 0 and 3 if ONE_BASED_INPUT = True
    0,3  -> chips 0 and 3 if ONE_BASED_INPUT = False
    """

    chips = []

    for item in text.split(","):
        item = item.strip()
        if not item:
            continue

        chip = int(item)

        if ONE_BASED_INPUT:
            chip -= 1

        if chip < 0 or chip >= MAX_CHIPS:
            raise ValueError("Chip numbers must be between 1 and 4.")

        chips.append(chip)

    return chips


# =============================
# Main GUI class
# =============================
class ThermalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Thermal Chip Live Monitor")

        self.ser = None
        self.running = False
        self.start_time = None

        self.selected_chips = []
        self.time_data = {}
        self.abs_data = {}
        self.rel_labels = {}
        self.lines = {}

        self.build_start_screen()

    def build_start_screen(self):
        frame = tk.Frame(self.root, padx=15, pady=15)
        frame.pack()

        tk.Label(frame, text="Serial Port:").grid(row=0, column=0, sticky="w")
        self.port_entry = tk.Entry(frame, width=18)
        self.port_entry.insert(0, "COM5")   # Windows example
        self.port_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Baud Rate:").grid(row=1, column=0, sticky="w")
        self.baud_entry = tk.Entry(frame, width=18)
        self.baud_entry.insert(0, "9600") # Default Baud Rate of 9600
        self.baud_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Chips to plot:").grid(row=2, column=0, sticky="w")
        self.chip_entry = tk.Entry(frame, width=18)
        self.chip_entry.insert(0, "1,4")
        self.chip_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(
            frame,
            text="Example: 1,4 means plot thermal chips 1 and 4"
        ).grid(row=3, column=0, columnspan=2, pady=5)

        self.status_label = tk.Label(frame, text="")
        self.status_label.grid(row=4, column=0, columnspan=2)

        start_button = tk.Button(frame, text="Start", command=self.start_gui)
        start_button.grid(row=5, column=0, columnspan=2, pady=10)

    def start_gui(self):
        try:
            port = self.port_entry.get().strip()
            baud = int(self.baud_entry.get().strip())
            self.selected_chips = parse_chip_input(self.chip_entry.get())

            self.ser = serial.Serial(port, baud, timeout=0.05)
            time.sleep(2)

        except Exception as e:
            self.status_label.config(text=f"Error: {e}")
            return

        for widget in self.root.winfo_children():
            widget.destroy()

        self.running = True
        self.start_time = time.time()

        self.time_data = {chip: deque(maxlen=1000) for chip in self.selected_chips}
        self.abs_data = {chip: deque(maxlen=1000) for chip in self.selected_chips}

        self.build_plot_screen()
        self.update_loop()

    def build_plot_screen(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        rel_frame = tk.Frame(main_frame, padx=10, pady=10)
        rel_frame.pack(side=tk.TOP, fill=tk.X)

        for chip in self.selected_chips:
            display_chip = chip + 1 if ONE_BASED_INPUT else chip

            label = tk.Label(
                rel_frame,
                text=f"Chip {display_chip} Relative Temperature: -- C",
                font=("Arial", 14)
            )
            label.pack(anchor="w")

            self.rel_labels[chip] = label

        self.fig = Figure(figsize=(8, 3 * len(self.selected_chips)), dpi=100)
        self.axes = {}

        for i, chip in enumerate(self.selected_chips):
            ax = self.fig.add_subplot(len(self.selected_chips), 1, i + 1)
            display_chip = chip + 1 if ONE_BASED_INPUT else chip

            ax.set_ylim(0, 50)
            ax.set_title(f"Chip {display_chip} Absolute Temperature")
            ax.set_xlabel("Time [s]")
            ax.set_ylabel("Abs Temp [C]")
            ax.grid(True)

            line, = ax.plot([], [], marker="o", markersize=3)

            self.axes[chip] = ax
            self.lines[chip] = line

        self.fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        stop_button = tk.Button(main_frame, text="Stop", command=self.stop)
        stop_button.pack(pady=5)

    def update_loop(self):
        if not self.running:
            return

        try:
            raw = self.ser.readline().decode(errors="ignore").strip()

            if raw:
                data = parse_serial_line(raw)
                t = time.time() - self.start_time

                for chip in self.selected_chips:
                    abs_key = f"temp_abs_{chip}"
                    rel_key = f"temp_rel_{chip}"

                    if abs_key in data:
                        self.time_data[chip].append(t)
                        self.abs_data[chip].append(data[abs_key])

                    if rel_key in data:
                        display_chip = chip + 1 if ONE_BASED_INPUT else chip
                        self.rel_labels[chip].config(
                            text=f"Chip {display_chip} Relative Temperature: {data[rel_key]:.2f} C"
                        )

                self.update_plots()

        except Exception as e:
            print("Serial read error:", e)

        self.root.after(100, self.update_loop)

    def update_plots(self):
        current_time = time.time() - self.start_time

        for chip in self.selected_chips:
            t_vals = list(self.time_data[chip])
            y_vals = list(self.abs_data[chip])

            if len(t_vals) == 0:
                continue

            # keep only last 60 seconds visible
            x_min = max(0, current_time - WINDOW_SECONDS)
            x_max = max(WINDOW_SECONDS, current_time)

            self.lines[chip].set_data(t_vals, y_vals)

            ax = self.axes[chip]
            ax.set_xlim(x_min, x_max)

            visible_y = [
                y for t, y in zip(t_vals, y_vals)
                if t >= x_min
            ]

            if visible_y:
                ymin = min(visible_y) - 1
                ymax = max(visible_y) + 1
                if ymin == ymax:
                    ymax += 1
                ax.set_ylim(ymin, ymax)

        self.canvas.draw_idle()

    def stop(self):
        self.running = False

        if self.ser is not None and self.ser.is_open:
            self.ser.close()

        self.root.destroy()


# =============================
# Run GUI
# =============================
if __name__ == "__main__":
    root = tk.Tk()
    app = ThermalGUI(root)
    root.mainloop()