import serial
import serial.tools.list_ports as ports
from datetime import datetime
import time
import csv

power = str(input("Enter Power Value in mW (e.g 500): "))

def read_data():
    # List available COM ports
    coms = ports.comports()
    for port in coms:
        print(f"{port.device} - {port.description}")

    # Ask user which COM port to use
    com = input("Choose COM port (e.g. COM3): ").strip()

    # Open serial connection
    ser = serial.Serial(port=com, baudrate=9600, timeout=1)

    file_name = f"Temp_Chip_Data_1/Arduino_Data_{power}mW.csv"
    count = 0

    # Open CSV file and write header
    with open(file_name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "temp_abs_0", "temp_rel_0", "temp_abs_1", "temp_rel_1"])

        print(f"\nLogging data to {file_name}...\nPress Ctrl+C to stop.\n")

        try:
            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()

                if line:
                    parts = line.split(",")

                    if len(parts) == 4:
                        # millis = parts[0]
                        temp_abs_0 = parts[0]
                        temp_rel_0 = parts[1]
                        temp_abs_1 = parts[2]
                        temp_rel_1 = parts[3]

                        timestamp = datetime.now().isoformat()

                        writer.writerow([timestamp, temp_abs_0, temp_rel_0, temp_abs_1, temp_rel_1])
                        f.flush()

                        print(timestamp,temp_abs_0, temp_rel_0, temp_abs_1, temp_rel_1)
                    else:
                        print(f"Bad data: {line}")
                time.sleep(0.5)
                count += 1
                if count >= 150:
                    break

        except KeyboardInterrupt:
            print("\nStopped by user.")

        finally:
            ser.close()
            print("Serial port closed.")


read_data()
