import matplotlib.pyplot as plt
from pandas import read_csv

# A script to visualize the results of the measurement study
#
# Requirements:
# python (tested with version 3.14.3)
# pandas (tested with version 3.0.2)
# matplotlib (tested with version 3.10.8)

# Read data and preprocess it

df = read_csv("./measurement_study/data/analyzed_servers_clean.csv")

df["command_mrulist"] = df["command_mrulist"].astype("category")
df["command_rv"] = df["command_rv"].astype("category")
df["command_pe"] = df["command_pe"].astype("category")

# First, handle data for stratum

stratum_plot = (
    df["ntp_stratum"]
    .value_counts()
    .plot(
        kind="pie", autopct="%.2f%%", fontsize=30, pctdistance=1.2, labeldistance=None
    )
)
stratum_plot.set_title("stratum", fontsize=30)
plt.legend(fontsize=30, loc="upper right", bbox_to_anchor=(1.14, 1.2))
plt.show()

# Then, process data of the used NTP version

version_plot = (
    df["ntp_version"]
    .value_counts()
    .plot(
        kind="pie", autopct="%.2f%%", fontsize=30, pctdistance=1.2, labeldistance=None
    )
)
version_plot.set_title("NTP version", fontsize=30)
plt.legend(fontsize=30, loc="upper right", bbox_to_anchor=(1.148, 1.1))
plt.show()

# Lastly, show data concerning the commands

commands_fig, (mrulist_plot, rv_plot, pe_plot) = plt.subplots(1, 3)
mrulist_plot.pie(
    df["command_mrulist"].value_counts(),
    autopct="%.2f%%",
    pctdistance=1.5,
    explode=(0, 0.2, 0),
)
rv_plot.pie(
    df["command_rv"].value_counts(),
    autopct="%.2f%%",
    pctdistance=1.3,
    explode=(0, 0.2),
)
pe_plot.pie(
    df["command_pe"].value_counts(),
    autopct="%.2f%%",
    pctdistance=1.3,
    explode=(0, 0.05, 0),
)
mrulist_plot.set_title("mrulist support")
rv_plot.set_title("rv support")
pe_plot.set_title("pe support")
plt.subplots_adjust(wspace=0.4)
plt.legend(
    fontsize=10,
    labels=df["command_pe"].value_counts().index,
    loc="upper right",
    bbox_to_anchor=(1.4, 1),
)
plt.show()
