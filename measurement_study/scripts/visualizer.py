import matplotlib.pyplot as plt
from pandas import read_csv

# A script to visualize the results of the measurement study
#
# Requirements:
# python (tested with version 3.14.3)
# pandas (tested with version 3.0.2)
# matplotlib (tested with version 3.10.8)

df = read_csv("./measurement_study/data/analyzed_servers_clean.csv")

df["command_mrulist"] = df["command_mrulist"].astype("category")
df["command_rv"] = df["command_rv"].astype("category")
df["command_pe"] = df["command_pe"].astype("category")

columns = ["command_mrulist", "command_rv", "command_pe", "ntp_version", "ntp_stratum"]

for col in columns:
    plot = df[col].value_counts().plot(kind="pie", autopct="%.2f", fontsize=20)
    plot.set_title(col, fontsize=20)
    plt.show()
