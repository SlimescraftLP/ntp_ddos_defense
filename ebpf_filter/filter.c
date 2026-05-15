#include <uapi/linux/bpf.h>
#include <uapi/linux/if_ether.h>
#include <uapi/linux/ip.h>
#include <uapi/linux/udp.h>

/*
A small eBPF program for rate-limiting NTP messages received on the host.
This is intended to be used in combination with the loader.py script, which
attaches this to the xdp hook.
Credits for most of the code go to SRodi on Github. Thank you!
https://github.com/SRodi/xdp-ddos-protect
*/

#define THRESHOLD 2 // Max packets per second
#define TIME_WINDOW_NS 1000000000 // 1 second in nanoseconds
#define NTP_PORT 123 // Standard port of the NTP protocol
#define IPPROTO_UDP 17 // UDP protocol number for IP

struct rate_limit_entry {
    __u64 last_update; // Timestamp of the last update
    __u32 packet_count; // Packet count within the time window
    __u64 packet_blocked; // Total packet count blocked from this host
};

BPF_HASH(rate_limit_map, __u32, struct rate_limit_entry, 1024);
BPF_HASH(exceptions_map, __u32, __u8, 1024);

int ddos_protection(struct xdp_md *ctx) {

    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;

    __u8 drop_flag = 0;

    // Parse Ethernet header
    struct ethhdr *eth = data;

    // Check if packet is large enough to contain Ethernet header
    if ((void *)(eth + 1) > data_end)
        return XDP_PASS;
    
    // Check for IP packets
    if (eth->h_proto != __constant_htons(ETH_P_IP))
        return XDP_PASS;

    // Parse IP header
    struct iphdr *iph = (void *)(eth + 1);

    // Check if ethernet frame is large enough to contain IP header
    if ((void *)(iph + 1) > data_end)
        return XDP_PASS;

    // Check for UDP message
    if (iph->protocol != IPPROTO_UDP)
        return XDP_PASS;
    
    // Parse UDP header
    struct udphdr *udp = (void *)(iph + 1);

    // Check if IP frame is large enough to contain UDP header
    if ((void *)(udp + 1) > data_end)
        return XDP_PASS;

    // Filter for NTP packets
    if (udp->source != __constant_htons(NTP_PORT) &&
        udp->dest   != __constant_htons(NTP_PORT))
        return XDP_PASS;
    
    // Parse NTP header
    __u8 *ntp = (void *)(udp + 1);

    // Check if UDP messages is large enough to contain NTP message
    if ((void *)(ntp + 1) > data_end)
        return XDP_PASS;


    //Extract mode of NTP message
    __u8 ntp_mode = *ntp & 0x07;

    //Mark mode 6 packets for DROP action
    if (ntp_mode == 6)
        drop_flag = 1;

    // Convert source IP from network to host byte order
    __u32 src_ip = __builtin_bswap32(iph->saddr);
    
    // Ignore violations if present in the list of exceptions
    __u8 *blocked = exceptions_map.lookup(&src_ip);
    if (blocked) {
        return XDP_PASS;
    }

    // Lookup rate limit entry for this IP
    struct rate_limit_entry *entry = rate_limit_map.lookup(&src_ip);
    
    // Get current time in nanoseconds
    __u64 current_time = bpf_ktime_get_ns();
    
    if (entry) {
        // Check if we're in the same time window
        if (current_time - entry->last_update < TIME_WINDOW_NS) {
            entry->packet_count++;
            if (entry->packet_count > THRESHOLD) {
                entry->packet_blocked++; //Increment the counter for blocked packets
                return XDP_DROP;
            }
        } else {
            // New time window, reset counter
            entry->last_update = current_time;
            entry->packet_count = 1;
        }
        // After handling entries, previous checks maybe need to drop it regardless of threshhold
        if (drop_flag == 1) {
            entry->packet_blocked++;
        return XDP_DROP;
    }
    } else {
        // Initialize rate limit entry for new IP
        struct rate_limit_entry new_entry;
        // Zero out padding bytes
        __builtin_memset(&new_entry, 0, sizeof(new_entry));
        new_entry.last_update = current_time;
        new_entry.packet_count = 1;
        if (drop_flag == 1){
            new_entry.packet_blocked = 1;
        } else {
            new_entry.packet_blocked = 0;
        }
        if (rate_limit_map.update(&src_ip, &new_entry) != 0) {
            return XDP_ABORTED; // Handle error if update fails
        }
        if (drop_flag == 1) {
            return XDP_DROP;
        }
    }
    return XDP_PASS; // Allow packet if under threshold   
}
