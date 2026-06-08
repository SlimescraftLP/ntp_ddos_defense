import matplotlib.pyplot as plt
from pandas import read_csv
import geopandas as gpd

# A script to visualize the results of the measurement study
#
# Requirements:
# python (tested with version 3.14.3)
# pandas (tested with version 3.0.2)
# matplotlib (tested with version 3.10.8)
# geopandas (tested with version 1.1.3)

# Read data and preprocess it

df = read_csv("./measurement_study/data/analyzed_servers_clean.csv")

df["command_mrulist"] = df["command_mrulist"].astype("category")
df["command_rv"] = df["command_rv"].astype("category")
df["command_pe"] = df["command_pe"].astype("category")

# Prepping for choropleth plot

iso_counts = (
    df["iso_code"]
    .value_counts()
    .reset_index()
)
iso_counts.columns = ["iso", "count"]

world_map = gpd.read_file(
    "./external_data/ne_110m_admin_0_countries.zip"
)

map_counts = world_map.merge(
    iso_counts,
    left_on="ISO_A2",
    right_on="iso",
    how="left"
)

map_counts["count"] = map_counts["count"].fillna(0)

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

# Continue with processing data of the used NTP version

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

# Then, show data concerning the commands

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

# Lastly, handle geographic data

fig, ax = plt.subplots(figsize=(15, 8))
# Handling countries without data
map_counts[map_counts["count"] == 0].plot(
    color="lightgrey",
    edgecolor="white",
    linewidth=0.3,
    ax=ax
)
# Handling the remaining countries
map_counts[map_counts["count"] > 0].plot(
    column="count",
    cmap="viridis",
    legend=True,
    edgecolor="white",
    linewidth=0.3,
    ax=ax
)
ax.axis("off")
plt.show()