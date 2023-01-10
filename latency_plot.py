import matplotlib.pyplot as plt
import pickle
import numpy as np

def plot_ping(ping_result_rina, ping_result_ip, title):
    rina_min = []
    rina_avg = []
    rina_max = []
    rina_mdev = []
    rina_x = []
    ip_min = []
    ip_avg = []
    ip_max = []
    ip_mdev = []
    ip_x = []
    
    result_rina = pickle.load(open(ping_result_rina, 'rb'))
    result_ip = pickle.load(open(ping_result_ip, 'rb'))

    for key in result_rina:
        rina_min.append(key[0])
        rina_avg.append(key[1])
        rina_max.append(key[2])
        rina_mdev.append(key[3])

    for key in result_ip:
        ip_min.append(key[0])
        ip_avg.append(key[1])
        ip_max.append(key[2])
        ip_mdev.append(key[3])

    plt.plot(rina_min, linestyle='dashed', marker='x', label = "RINA minimum latency")
    plt.plot(rina_avg, linestyle='dashed', marker='D', label = "RINA average latency")
    plt.plot(rina_max, linestyle='dashed', marker='o', label = "RINA maximum latency")
    plt.plot(rina_mdev, linestyle='dashed', marker='^', label = "RINA deviation latency")

    plt.plot(ip_min, marker='x', label = "IP minimum latency")
    plt.plot(ip_avg, marker='D', label = "IP average latency")
    plt.plot(ip_max, marker='o', label = "IP maximum latency")
    plt.plot(ip_mdev, marker='^', label = "IP deviation latency")
    
    plt.xlabel('Current Node')
    plt.ylabel('Latency in miliseconds')
    plt.xticks(np.arange(0, len(result_rina), 1))
    plt.title(title)
    plt.legend()
    plt.show()

def plot_rr(rr_result_rina, rr_result_tcp, rr_result_udp, title):
    raw_result_rina = pickle.load(open(rr_result_rina, 'rb'))
    raw_result_tcp = pickle.load(open(rr_result_tcp, 'rb'))
    raw_result_udp = pickle.load(open(rr_result_udp, 'rb'))

    print(f'raw_result_rina in nanosecounds {raw_result_rina}')
    print(f'raw_result_tcp in microseconds {raw_result_tcp}')
    print(f'raw_result_udp in microseconds {raw_result_udp}')

    result_rina = [item * pow(10, -6) for item in raw_result_rina]
    result_tcp = [item * pow(10, -3) for item in raw_result_tcp]
    result_udp = [item * pow(10, -3) for item in raw_result_udp]

    print(f'result_rina in millisecounds {result_rina}')
    print(f'result_tcp in milliseconds {result_tcp}')
    print(f'result_udp in milliseconds {result_udp}')

    plt.plot(result_rina, linestyle='dashed', marker='x', label = 'RINA rr')
    plt.plot(result_tcp, marker='D', label = 'TCP rr')
    plt.plot(result_udp, marker='o', label = 'UDP rr')

    plt.xlabel('Current Node')
    plt.ylabel('Latency in miliseconds')
    plt.xticks(np.arange(0, len(result_rina), 1))
    plt.title(title)
    plt.legend()
    plt.show()

    


def main():
    plot_ping("line_ping_result_rina", "line_ping_result_ip", "Ping latency line topology")
    plot_ping("redundant_ping_result_rina", "redundant_ping_result_ip", "Ping latency redundant topology")
    plot_ping('fully_meshed_ping_result_rina', 'fully_meshed_ping_result_ip', 'Ping latency fully meshed topology')

    plot_rr('line_rr_result_rina', 'line_rr_tcp_result', 'line_rr_udp_result', 'Line Request/Response (rr)')
    plot_rr('redundant_rr_result_rina', 'redundant_rr_tcp_result', 'redundant_rr_udp_result', 'Redundant Request/Response (rr)')
    plot_rr('fully_meshed_rr_result_rina', 'fully_meshed_rr_tcp_result', 'fully_meshed_rr_udp_result', 'Fully meshed Request/Response (rr)')

if __name__ == "__main__":
    main()