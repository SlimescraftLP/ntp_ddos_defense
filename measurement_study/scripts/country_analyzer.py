from pandas import DataFrame, read_csv

# A small script to analyze the the values for country in the analyzed_servers_clean.csv
#
# Requirements:
# python (tested with version 3.14.3)
# pandas (tested with version 3.0.2)

df = read_csv("measurement_study/data/analyzed_servers_clean.csv", index_col=0)

vc = df["country"].value_counts().head(10)
result = DataFrame({"Counts": vc, "Percent": vc / len(df) * 100})
print(f"Total different countries: {df['country'].value_counts().count()}")
print("Top Values:")
print(result)
