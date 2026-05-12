from bcc import BPF
import signal, time, sys

# A simple loader for the eBPF program included in this repository using BCC.
# Currently, the interface is hardcoded. This will get an update soon.

iface = "docker0"

b = BPF(src_file="ebpf_filter/filter.c")
fx = b.load_func("ddos_protection", BPF.XDP)
BPF.attach_xdp(iface,fx,0)

print(f"Successfully started XDP program on interface {iface}. Listening...")

def cleanup(sig=None, frame=None):
    print("\nDetaching XDP program...")
    b.remove_xdp(iface, 0)
    print("XDP program successfully detached. Exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

try:
    b.trace_print()
except KeyboardInterrupt:
    cleanup()