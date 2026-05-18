from time import time
from os.path import dirname
import psutil
import pandas as pd
import matplotlib.pyplot as plt

# Script to monitor the cpu of the system by core. It will output the recorded data as a csv file 
# and two images containing an over-time and averages visualization. This script expects a "data" 
# directory in the same location it is placed in.

def observe():
    data = []
    start_time = round(time(),2)
    try:
        while True:
            delta_time = round(time(),2) - start_time
            core_usages = psutil.cpu_percent(interval=0.25, percpu=True)
            row = {"delta_time": round(delta_time, 2)}
            for i, usage in enumerate(core_usages):
                row[f"core_{i}_percent"] = usage
            data.append(row)
    except KeyboardInterrupt:
        pass
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
    plt.savefig(f"{output_dir}core_usages.png")
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
    plt.savefig(f"{output_dir}core_averages.png")
    plt.close()


def main():
    print("Started observer. Stop with CTRL-C.")
    df = observe()
    print("\nSuccessfully stopped observer. Calculating and outputting results...")
    data_dir = f"{dirname(__file__)}/data/"
    df.to_csv(f"{data_dir}cpu_usage.csv", index=False)
    visualize_core_usages(df, data_dir)
    visualize_averages(df, data_dir)
    print("Completed outputting. Exiting...")


if __name__ == "__main__":
    main()