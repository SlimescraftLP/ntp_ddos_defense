from scapy.all import *
from scapy.layers.ntp import NTP
from time import sleep

# Short script for generating a bulk of custom NTP traffic.
# It requires the testcase to run as an argument and communicates on port 9999 UDP with the observer script.
# Configuration parameters are listed below and can be altered as seen fit:

##########################################################################################################

target_ip="127.0.0.1"   # IP of the NTP server
sender_ip="0.0.0.0"     # Spoofed IP address of the sender. Useful for simulation of amplification attack.
interface="lo"          # Name of network interface to use

##########################################################################################################

def test(mode,amount):
    pkt = (
        Ether()/
        IP(dst=target_ip,src=sender_ip)/
        UDP(sport=12345,dport=123)/
        NTP(
            mode=mode
        )
    )
    sendpfast(pkt,count=amount,iface=interface)

def main(testcase):
    # Signal start of measurement
    send(IP(dst=target_ip)/UDP(dport=9999)/Raw(load=b"START"))
    sleep(1)
    match testcase:
        case 1:
            test(6,1000000)
        case 2:
            test(6,10000000)
        case 3:
            test(4,1000000)
        case 4:
            test(4,10000000)
        case _:
            sys.exit("Error: Testcase not known")
    sleep(1)
    # Signal end of measurement
    send(IP(dst=target_ip)/UDP(dport=9999)/Raw(load=b"STOP"))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Error: wrong number of arguments")
    testcase = int(sys.argv[1])
    main(testcase)