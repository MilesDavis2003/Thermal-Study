import socket
import serial
import serial.tools.list_ports as coms
from datetime import datetime
import schedule
import time as t
import csv

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("192.168.1.13", 5025))

scpi_command = "*IDN?".encode()
print(sock.sendall(scpi_command))
#print(sock.recv(1024).decode.split("\n")[0])

ports = coms.comports()
for port in ports:
    print(f"Device: {port.device}, Description: {port.description}, HARDWARE ID: {port.hwid}")
    print("-"*50)
print()
com_name = str(input("Choose COM port (e.g. /dev/ttyS0): "))

ser = serial.Serial(com_name, 9600, timeout = 1)

#while True:
#    line = ser.readline().decode('utf-8').strip()
#    if line:
#        t.sleep(0.5)
#        print(line)

file_name = "/home/datataking/Desktop/stave_temp_measure/Temp_Volt_time_data.csv"

seconds = 0
start_time = 0
with open(file_name, 'w', newline="") as f:
    writer = csv.writer(f)
    # S is for series and P is for parallel
    writer.writerow(['timestamp','time','volt_S','temp_S','volt_P', 'temp_P', 'temp_chmbr'])
    temp_chmbr = 0
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line:
            #t.sleep(0.5)
            scpi_command = f":SOURCE:CLOOP1:SPOINT {temp_chmbr}"
            sock.sendall(scpi_command.encode())
            
            parts = line.split(",")
            print(parts)
            timestamp = datetime.now().isoformat()
            if len(parts) == 5:
                time = parts[0]
                volt_S = parts[1]
                temp_S = parts[2]
                volt_P = parts[3]
                temp_P = parts[4]
            else:
                continue
            
            writer.writerow([timestamp, time, volt_S, temp_S, volt_P, temp_P, temp_chmbr])
            f.flush()
        sec_ = 5
        if start_time <= 3500:
            t.sleep(sec_)
            start_time += sec_
        else:
            seconds += sec_
            t.sleep(sec_)
            if seconds % 1800 == 0:
                temp_chmbr += 5
                print(temp_chmbr)
                if temp_chmbr > 50:
                    break
        
