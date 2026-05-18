from bcc import BPF
import time, sys, os
from struct import pack, unpack
from socket import inet_ntoa,inet_aton
from curses import wrapper,curs_set
from ctypes import c_uint32,c_uint8

# A loader for the NTP DDoS protection eBPF program included in this repository using BCC.
# It takes 1 argument, which is the name of the intended network interface.
# An additional list of exceptions for this filter can be set in the "exceptions.conf" file.
# This needs the python BCC interface, which can be aquired from their 
# Github repository or by installing the dedicated package shipped with 
# most common Linux distributions. Examples for references to these are:
#
# Github: https://github.com/iovisor/bcc
# Debian: https://packages.debian.org/sid/python3-bpfcc
# Arch: https://archlinux.org/packages/extra/x86_64/python-bcc/
# RHEL: https://pkgs.org/download/python3-bcc

b = BPF(src_file=f"{os.path.dirname(__file__)}/filter.c")
fx = b.load_func("ddos_protection", BPF.XDP)

def cleanup(stdscr):
    stdscr.clear()
    stdscr.addstr("Detaching XDP program...")
    stdscr.refresh()
    b.remove_xdp(iface, 0)
    stdscr.addstr("\nXDP program successfully detached. Exiting in 3...")
    stdscr.refresh()
    time.sleep(3)
    sys.exit(0)

def main(stdscr):
    with open(f"{os.path.dirname(__file__)}/exceptions.conf") as f:
        exceptions = [line.rstrip('\n') for line in f]

    for ip in exceptions:
        ip_u32 = unpack("!I", inet_aton(ip))[0]
        key = c_uint32(ip_u32)
        value = c_uint8(1)
        b["exceptions_map"][key] = value
    curs_set(0)
    stdscr.clear()
    stdscr.addstr(f"Loaded {len(exceptions)} exceptions for the filter.\n")
    stdscr.refresh()
    BPF.attach_xdp(iface,fx,0)
    stdscr.addstr(f"Successfully started XDP program on interface {iface}. Switching to overview in 3...")
    stdscr.refresh()
    time.sleep(3)

    try:
        while True:
            stdscr.clear()
            stdscr.addstr("Status: Active\n\nPeers:\t\t|\tBlocked packets:\n")
            stdscr.addstr(3, 0, "-" * 40)
            stdscr.addstr("\n")
            map_output = b["rate_limit_map"].items()
            for item in map_output:
                stdscr.addstr(f"{inet_ntoa(pack("!I", item[0].value))}\t|\t {item[1].packet_blocked}\n")
            stdscr.refresh()
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup(stdscr)

if len(sys.argv) != 2:
    print("Error: wrong number of arguments")
    sys.exit(0)

iface = sys.argv[1]

wrapper(main)