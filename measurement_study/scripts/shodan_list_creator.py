from os import getenv

from dotenv import load_dotenv
from pandas import DataFrame
from shodan import APIError, Shodan

# script for creating a list of public NTP servers using shodan.
# Currently limited to the first 50 pages of results, which contain
# 100 entries each. To use this script, the environment variable "SHODAN_API_KEY"
# must be set to a valid shodan account API key, that has permissions for the usage
# of the "search"-API-endpoint.
#
# Requirements:
# python (tested with version 3.14.3)
# pandas (tested with version 3.0.2)
# shodan (tested with version 1.31.0)
#
# for simplicity, the package python-dotenv (tested with version 1.2.2) is used to
# import the environment variable. This is not a hard requirement for the use case
# but the current code relies on its presence.


def create_list() -> DataFrame:
    api = Shodan(getenv("SHODAN_API_KEY"))
    df = DataFrame(
        {
            "ip": [],
            "hostnames": [],
            "ntp_product": [],
            "ntp_stratum": [],
            "ntp_version": [],
            "ntp_precision": [],
            "ntp_rootdelay": [],
            "ntp_rootdisp": [],
            "ntp_ref_id": [],
        }
    )
    for i in range(1, 51):
        print(f"Running page {i}")
        try:
            search_result = api.search(query="port:123", page=i)
        except APIError as e:
            print(f"Error while using API at page index {i}: {str(e)}")
        else:
            for host in search_result["matches"]:
                ip = host.get("ip_str", "unknown")
                hostnames = ", ".join(host.get("hostnames", [])) or "unknown"
                ntp_product = host.get("product", "unknown")
                ntp_section = host.get("ntp", {})
                ntp_stratum = ntp_section.get("stratum", "unknown")
                ntp_version = ntp_section.get("version", "unknown")
                ntp_precision = ntp_section.get("precision", "unknown")
                ntp_rootdelay = ntp_section.get("root_delay", "unknown")
                ntp_rootdisp = ntp_section.get("root_dispersion", "unknown")
                ntp_ref_id = ntp_section.get("refid", "unknown")

                new_data = {
                    "ip": ip,
                    "hostnames": hostnames,
                    "ntp_product": ntp_product,
                    "ntp_stratum": ntp_stratum,
                    "ntp_version": ntp_version,
                    "ntp_precision": ntp_precision,
                    "ntp_rootdelay": ntp_rootdelay,
                    "ntp_rootdisp": ntp_rootdisp,
                    "ntp_ref_id": ntp_ref_id,
                }
                df.loc[len(df)] = new_data
    return df


if __name__ == "__main__":
    load_dotenv()
    data = create_list()
    data.to_csv("./measurement_study/data/ntp_server_list.csv")
