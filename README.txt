This repository contains work on a NTP DDoS filter using eBPF/XDP. It is part of the practical work on my master thesis.
The repo contains a measurement study on public NTP servers to motivate the need for such a filter as well as an implementation of a proof of concept.

The folder structure presents itself as follows:

ntp_ddos_defense
|
| - ebpf_filter             - POC implementation of the filter.
| - external_data           - Folder for external datasets. Needed by scripts of the measurement study.
| - measurement_study       - Folder containing scripts and data of the measurement study.
|   |
|   | - data                - The datasets created during the measurement study.
|   | - scripts             - All scripts used during the study.
|
| - test_scripts            - Scripts for testing and benchmarking the POC implementation.
| - README.txt              - This file