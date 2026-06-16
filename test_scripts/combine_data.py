import sys
import matplotlib.pyplot as plt
from pandas import read_csv
from os.path import dirname

def draw_cpu_comparison(df1,df2,output_dir):
    plt.figure(figsize=(10, 5))
    plt.plot(df1["delta_time"], df1["cpu_percent"],label="iptables")
    plt.plot(df2["delta_time"], df2["cpu_percent"],label="eBPF")
    plt.xlabel("Time")
    plt.ylabel("CPU usage in %")
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{output_dir}combined_cpu.pdf")

def draw_cycle_comparison(dict1,dict2,output_dir):
    plt.figure(figsize=(5, 4))
    plt.bar(["iptables","eBPF"], [(int(dict1["cycles"])/1e9),(int(dict1["cycles"])/1e9)])
    plt.ylabel('Cycles in billions')
    plt.title('Comparison between CPU cycles')
    plt.savefig(f"{output_dir}combined_cycle.pdf")

def draw_instruction_comparison(dict1,dict2,output_dir):
    plt.figure(figsize=(5, 4))
    plt.bar(["iptables","eBPF"], [(int(dict1["instructions"])/1e9),(int(dict1["instructions"])/1e9)])
    plt.ylabel('Instructions in billions')
    plt.title('Comparison between CPU instructions')
    plt.savefig(f"{output_dir}combined_instruction.pdf")

def main(dir1,dir2):
    df1 = read_csv(f"{dir1}/cpu_usage.csv")
    df2 = read_csv(f"{dir2}/cpu_usage.csv")
    data_dir = f"{dirname(__file__)}/data/"
    with open(f"{dir1}/perf.txt","r") as f:
        perf_txt1 = dict()
        for line in f:
            line = line.strip()
            key, value = line.split(":")
            perf_txt1[key] = value
    with open(f"{dir2}/perf.txt","r") as f:
        perf_txt2 = dict()
        for line in f:
            line = line.strip()
            key, value = line.split(":")
            perf_txt2[key] = value
    draw_cpu_comparison(df1,df2,data_dir)
    draw_cycle_comparison(perf_txt1,perf_txt2,data_dir)
    draw_instruction_comparison(perf_txt1,perf_txt2,data_dir)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Error: wrong number of arguments")
    dir1 = sys.argv[1]
    dir2 = sys.argv[2]
    main(dir1,dir2)