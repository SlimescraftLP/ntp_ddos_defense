from time import time
from os.path import dirname, isfile
import psutil
import pandas as pd
import matplotlib.pyplot as plt
import subprocess
import os
import matplotlib as mpl
import socket
import threading

# Script to monitor the cpu of the system by core. It will output the recorded data as a csv file 
# and two images containing an over-time and averages visualization in addition to a textfile 
# containing cpu cycles and instructions. This script expects a "data" directory in the same 
# location it is placed in.

observing_flag = threading.Event()
stop_flag = threading.Event()

def control_thread():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 9999))
    while not stop_flag.is_set():
        data, addr = sock.recvfrom(1024)
        msg = data.decode()
        if msg == "START":
            observing_flag.set()
        if msg == "STOP":
            observing_flag.clear()

def observe():
    data = []
    start_time = round(time(),2)
    while observing_flag.is_set():
        delta_time = round(time(),2) - start_time
        cpu_usage = psutil.cpu_percent(interval=0.25)
        core_usages = psutil.cpu_percent(interval=0.25, percpu=True)
        row = {
            "delta_time": round(delta_time, 1),
            "cpu_percent": cpu_usage
        }
        for i, usage in enumerate(core_usages):
            row[f"core_{i}_percent"] = usage
        data.append(row)
    return pd.DataFrame(data)

def visualize_core_usages(df, output_dir):
    core_columns = [c for c in df.columns if c.startswith("core_")]
    max_value = df[core_columns].max().max()
    ylim = min(100, max_value * 1.1)
    plt.figure(figsize=(12, 6))

    for col in core_columns:
        label = (
            col.replace("_percent", "")
               .replace("_", " ")
               .title()
        )

        plt.plot(df["delta_time"], df[col], label=label)

    plt.xlabel("Time elapsed")
    plt.ylabel("Core usage in percent")
    plt.title("Core usages over time")
    plt.ylim(0, ylim)
    plt.grid(True)
    plt.legend(ncol=2)
    plt.tight_layout()
    plt.savefig(f"{output_dir}core_usages.pdf")
    plt.close()


def visualize_averages(df, output_dir):
    core_columns = [c for c in df.columns if c.startswith("core_")]
    averages = df[core_columns].mean()
    labels = [
        c.replace("_percent", "")
         .replace("_", " ")
         .title()
        for c in core_columns
    ]
    max_value = averages.max()
    ylim = min(100, max_value * 1.1)

    plt.figure(figsize=(10, 6))
    plt.bar(labels, averages)
    plt.xlabel("Core")
    plt.ylabel("Average usage in percent")
    plt.title("Average core usages over time")
    plt.ylim(0, ylim)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}core_averages.pdf")
    plt.close()

def save_perf(data,output_dir):
    output = []
    for i,line in enumerate(data.splitlines()):
        words = line.split()
        if i == 0:
            output.append(f"time:{words[2]}")
        output.append(f"{words[1]}:{words[0]}")
    with open(f"{output_dir}perf.txt","a") as f:
        for line in output:
            f.write(f"{line}\n")

def cleanup(output_dir):
    if isfile(f"{output_dir}cpu_usage.csv"):
        os.remove(f"{output_dir}cpu_usage.csv")
    if isfile(f"{output_dir}core_usages.pdf"):
        os.remove(f"{output_dir}core_usages.pdf")
    if isfile(f"{output_dir}core_averages.pdf"):
        os.remove(f"{output_dir}core_averages.pdf")
    if isfile(f"{output_dir}perf.txt"):
        os.remove(f"{output_dir}perf.txt")

def main():
    data_dir = f"{dirname(__file__)}/data/"
    cleanup(data_dir) # Clear previous attempts
    thread = threading.Thread(target=control_thread, daemon=True) 
    thread.start()
    print("Waiting for start signal...")
    while True:
        if observing_flag.is_set():
            break
    print("Started observer. Running until stop signal is received.")
    perf_process = subprocess.Popen(
        ["perf","stat","-a", "-e", "cycles,instructions","-x"," "],
        stderr=subprocess.PIPE,
        text=True
    )
    df = observe()
    perf_process.send_signal(subprocess.signal.SIGINT)
    print("Successfully stopped observer. Calculating and outputting results...")
    stop_flag.set()
    df.to_csv(f"{data_dir}cpu_usage.csv", index=False)
    visualize_core_usages(df, data_dir)
    visualize_averages(df, data_dir)
    _, perf_output = perf_process.communicate()
    save_perf(perf_output,data_dir)
    print("Completed outputting. Exiting...")


if __name__ == "__main__":
    mpl.use("Agg")
    main()