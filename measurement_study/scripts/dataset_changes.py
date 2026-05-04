from pandas import read_csv

# A script to sanitize the analyzed_servers.csv
#
# Requirements:
# python (tested with version 3.14.3)
# pandas (tested with version 3.0.2)

df = read_csv("./measurement_study/data/analyzed_servers.csv", index_col=0)

df["ntp_stratum"] = df["ntp_stratum"].where(
    df["ntp_stratum"].isin([3, 2, 4, 0, 5, 16]), "other"
)

df["ntp_version"] = df["ntp_version"].str.replace('"', "", regex=False)

df["ntp_version"] = df["ntp_version"].where(
    df["ntp_version"].isin(["3", "4"]), "other/unknown"
)

df.to_csv("./measurement_study/data/analyzed_servers_clean.csv")
