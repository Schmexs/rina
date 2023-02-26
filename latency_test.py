#!/usr/bin/python3

import subprocess
import rina
import logging
import time
import re
import statistics
import json

lo = logging.getLogger("rina")

nodeCountList = [3, 5]
#nodeCountList = [5, 10, 20, 40, 65]
LINE_SIZES = [2, 5, 10, 20]
MESH_SIZES = [5, 10, 30]
REDUNDANT_SIZES = [5, 10, 30]
nodeCount = 2
pingCount = 10
rrTransactions = 100

regex_ping_raw = re.compile('([0-9]+\.[0-9]+/){3}[0-9]+\.[0-9]+')
regex_ping = re.compile('[\d.]+')
regex_rinaperf_rr = re.compile('Sender\s*\d*\s*[\d\.]*\s*[\d\.]*\s*([\d]*)')
regex_netperf_rr = re.compile('[0-9\.]*')

###arrays line_latency_test###
#RINA
line_ping_result_rina = {}
line_ping_result_rina_min = {}
line_ping_result_rina_avg = {}
line_ping_result_rina_max = {}
line_ping_result_rina_mdev = {}
line_rr_result_rina = {}
#IP
line_ping_result_ip = {}
line_ping_result_ip_min = {}
line_ping_result_ip_avg = {}
line_ping_result_ip_max = {}
line_ping_result_ip_mdev = {}
line_rr_tcp_result = {}
line_rr_udp_result = {}

###arrays redundant_latency_test###
#RINA
redundant_ping_result_rina = {}
redundant_ping_result_rina_min = {}
redundant_ping_result_rina_avg = {}
redundant_ping_result_rina_max = {}
redundant_ping_result_rina_mdev = {}
redundant_rr_result_rina = {}
#IP
redundant_ping_result_ip = {}
redundant_ping_result_ip_min = {}
redundant_ping_result_ip_avg = {}
redundant_ping_result_ip_max = {}
redundant_ping_result_ip_mdev = {} 
redundant_rr_tcp_result = {}
redundant_rr_udp_result = {}

###arrays fully_meshed_latency_test###
#RINA
fully_meshed_ping_result_rina = {}
fully_meshed_ping_result_rina_min = {}
fully_meshed_ping_result_rina_avg = {}
fully_meshed_ping_result_rina_max = {}
fully_meshed_ping_result_rina_mdev = {}
fully_meshed_rr_result_rina = {}
#IP
fully_meshed_ping_result_ip = {}
fully_meshed_ping_result_ip_min = {} 
fully_meshed_ping_result_ip_avg = {}
fully_meshed_ping_result_ip_max = {}
fully_meshed_ping_result_ip_mdev = {}
fully_meshed_rr_tcp_result = {}
fully_meshed_rr_udp_result = {}

def plot(ping_result_rina_min, 
ping_result_rina_avg, 
ping_result_rina_max, 
ping_result_rina_mdev, 
rr_result_rina, 
ping_result_ip_min,
ping_result_ip_avg,
ping_result_ip_max,
ping_result_ip_mdev, 
rr_result_tcp, 
rr_result_udp, title) -> dict:
    series = []
    size = []
    node = []

    all_ping_series = []
    all_rr_series = []

    maxnode = len(ping_result_rina_min)

    for key in ping_result_rina_min:
        s = int(key.split(':')[0])
        size.append(s) if s not in size else None

    for s in size:
        x = []

        for node in range(s):
            x.append(node) if x not in x else None

        rina_series_ping_min = {
            'name': f'{s}-nodes - RINA Ping Min',
            'data': list((x[i], ping_result_rina_min[f'{s}:{i}']) for i in range(len(x))),
            'dashed': False
        }
        rina_series_ping_avg = {
            'name': f'{s}-nodes - RINA Ping Avg',
            'data': list((x[i], ping_result_rina_avg[f'{s}:{i}']) for i in range(len(x))),
            'dashed': False
        }
        rina_series_ping_max = {
            'name': f'{s}-nodes - RINA Ping Max',
            'data': list((x[i], ping_result_rina_max[f'{s}:{i}']) for i in range(len(x))),
            'dashed': False
        }
        rina_series_ping_mdev = {
            'name': f'{s}-nodes - RINA Ping mdev',
            'data': list((x[i], ping_result_rina_mdev[f'{s}:{i}']) for i in range(len(x))),
            'dashed': False
        }

        rina_series_rr = {
            'name': f'{s}-nodes - RINA rr',
            'data': list((x[i], rr_result_rina[f'{s}:{i}']) for i in range(len(x))),
            'dashed': False
        }

        ip_series_ping_min = {
            'name': f'{s}-nodes - IP Ping Min',
            'data': list((x[i], ping_result_ip_min[f'{s}:{i}']) for i in range(len(x))),
            'dashed': True
        }
        ip_series_ping_avg = {
            'name': f'{s}-nodes - IP Ping Avg',
            'data': list((x[i], ping_result_ip_avg[f'{s}:{i}']) for i in range(len(x))),
            'dashed': True
        }
        ip_series_ping_max = {
            'name': f'{s}-nodes - IP Ping Max',
            'data': list((x[i], ping_result_ip_max[f'{s}:{i}']) for i in range(len(x))),
            'dashed': True
        }
        ip_series_ping_mdev = {
            'name': f'{s}-nodes - IP Ping mdev',
            'data': list((x[i], ping_result_ip_mdev[f'{s}:{i}']) for i in range(len(x))),
            'dashed': True
        }

        tcp_series_rr = {
            'name': f'{s}-nodes - TCP rr',
            'data': list((x[i], rr_result_tcp[f'{s}:{i}']) for i in range(len(x))),
            'dashed': True
        }

        udp_series_rr = {
            'name': f'{s}-nodes - UDP rr',
            'data': list((x[i], rr_result_udp[f'{s}:{i}']) for i in range(len(x))),
            'dashed': True
        }

        all_ping_series.append(rina_series_ping_min)
        all_ping_series.append(rina_series_ping_avg)
        all_ping_series.append(rina_series_ping_max)
        all_ping_series.append(rina_series_ping_mdev)
        all_ping_series.append(ip_series_ping_min)
        all_ping_series.append(ip_series_ping_avg)
        all_ping_series.append(ip_series_ping_max)
        all_ping_series.append(ip_series_ping_mdev)
        all_rr_series.append(rina_series_rr)
        all_rr_series.append(tcp_series_rr)
        all_rr_series.append(udp_series_rr)
     
    #series = all_ping_series + all_rr_series

    return [{f'{title} {maxnode} rr':all_rr_series},{f'{title} {maxnode} ping':all_ping_series}]

def line_latency_test():
    global nodeCount

    line_ping_result_rina = {}
    line_ping_result_rina_min = {}
    line_ping_result_rina_avg = {}
    line_ping_result_rina_max = {}
    line_ping_result_rina_mdev = {}
    line_rr_result_rina = {}
    line_ping_result_ip = {}
    line_ping_result_ip_min = {}
    line_ping_result_ip_avg = {}
    line_ping_result_ip_max = {}
    line_ping_result_ip_mdev = {}
    line_rr_tcp_result  = {}
    line_rr_udp_result  = {}

    lo.info(f"Running latency test with line topology wit {nodeCount} nodes.")

    rina.create_networknamespaces(nodeCount)
    rina.create_line_topology(nodeCount)
    time.sleep(nodeCount)

    rina.run('bash', '-c', 'rinaperf -l -d n.DIF &', netns='node0')
    rina.run('netserver', netns='node0')
    
    for currentNode in range(nodeCount):
        #RINA
        raw_line_ping_result_rina = re.search(regex_ping_raw, rina.run('rinaperf', '-d', 'n.DIF', 'ping','-D', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        line_ping_result_rina[f'{nodeCount}:{currentNode}'] = list(map(float, re.findall(regex_ping, raw_line_ping_result_rina)))
        line_ping_result_rina_min[f'{nodeCount}:{currentNode}'] = line_ping_result_rina[f'{nodeCount}:{currentNode}'][0]
        line_ping_result_rina_avg[f'{nodeCount}:{currentNode}'] = line_ping_result_rina[f'{nodeCount}:{currentNode}'][1]
        line_ping_result_rina_max[f'{nodeCount}:{currentNode}'] = line_ping_result_rina[f'{nodeCount}:{currentNode}'][2]
        line_ping_result_rina_mdev[f'{nodeCount}:{currentNode}'] = line_ping_result_rina[f'{nodeCount}:{currentNode}'][3]
        line_rr_result_rina[f'{nodeCount}:{currentNode}'] = round(float(re.findall(regex_rinaperf_rr ,rina.run('rinaperf', '-d', 'n.DIF', '-c', rrTransactions, '-t', 'rr', netns=f'node{currentNode}', stdout=subprocess.PIPE))[0]) * pow(10, -6), 4)

        #IP
        console_output_ping_ip = rina.run('ping', '10.0.0.1', '-q', '-c', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)
        raw_line_ping_result_ip = re.search(regex_ping_raw, console_output_ping_ip).group(0)
        line_ping_result_ip[f'{nodeCount}:{currentNode}'] = list(map(float, re.findall(regex_ping, raw_line_ping_result_ip)))
        line_ping_result_ip_min[f'{nodeCount}:{currentNode}'] = line_ping_result_ip[f'{nodeCount}:{currentNode}'][0]
        line_ping_result_ip_avg[f'{nodeCount}:{currentNode}'] = line_ping_result_ip[f'{nodeCount}:{currentNode}'][1]
        line_ping_result_ip_max[f'{nodeCount}:{currentNode}'] = line_ping_result_ip[f'{nodeCount}:{currentNode}'][2]
        line_ping_result_ip_mdev[f'{nodeCount}:{currentNode}'] = line_ping_result_ip[f'{nodeCount}:{currentNode}'][3]

        console_output_rr_tcp = rina.run('netperf', '-H', '10.0.0.1', '-P', '0' '-t', 'TCP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)
        console_output_rr_ip = rina.run('netperf', '-H', '10.0.0.1', '-P', '0' '-t', 'UDP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)
        line_rr_tcp_result[f'{nodeCount}:{currentNode}'] = round(float(re.search(regex_netperf_rr, console_output_rr_tcp).group(0)) * pow(10, -3), 4)
        line_rr_udp_result[f'{nodeCount}:{currentNode}'] = round(float(re.search(regex_netperf_rr, console_output_rr_ip).group(0)) * pow(10, -3), 4)

    return (plot(line_ping_result_rina_min,
    line_ping_result_rina_avg,
    line_ping_result_rina_max,
    line_ping_result_rina_mdev, 
    line_rr_result_rina, 
    line_ping_result_ip_min,
    line_ping_result_ip_avg,
    line_ping_result_ip_max,
    line_ping_result_ip_mdev,  
    line_rr_tcp_result, 
    line_rr_udp_result,  
    f'latency line topology'))

def redundant_latency_test():
    global nodeCount

    redundant_ping_result_rina = {}
    redundant_ping_result_rina_min = {}
    redundant_ping_result_rina_avg = {}
    redundant_ping_result_rina_max = {}
    redundant_ping_result_rina_mdev = {}
    redundant_rr_result_rina = {}
    redundant_ping_result_ip = {}
    redundant_ping_result_ip_min = {}
    redundant_ping_result_ip_avg = {}
    redundant_ping_result_ip_max = {}
    redundant_ping_result_ip_mdev = {}
    redundant_rr_tcp_result = {}
    redundant_rr_udp_result = {}

    lo.info(f"Running latency test with redundant topology with {nodeCount} nodes.")

    rina.create_networknamespaces(nodeCount)
    rina.create_redundant_paths_topology(nodeCount)
    time.sleep(nodeCount)

    rina.run('bash', '-c', 'rinaperf -l -d n.DIF &', netns='node0')
    rina.run('netserver', netns='node0')

    for currentNode in range(nodeCount):
        #RINA
        raw_redundant_ping_result_rina = re.search(regex_ping_raw, rina.run('rinaperf', '-d', 'n.DIF', 'ping','-D', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        redundant_ping_result_rina[f'{nodeCount}:{currentNode}'] = list(map(float, re.findall(regex_ping, raw_redundant_ping_result_rina)))
        redundant_ping_result_rina_min[f'{nodeCount}:{currentNode}'] = redundant_ping_result_rina[f'{nodeCount}:{currentNode}'][0]
        redundant_ping_result_rina_avg[f'{nodeCount}:{currentNode}'] = redundant_ping_result_rina[f'{nodeCount}:{currentNode}'][1]
        redundant_ping_result_rina_max[f'{nodeCount}:{currentNode}'] = redundant_ping_result_rina[f'{nodeCount}:{currentNode}'][2]
        redundant_ping_result_rina_mdev[f'{nodeCount}:{currentNode}'] = redundant_ping_result_rina[f'{nodeCount}:{currentNode}'][3]
        redundant_rr_result_rina[f'{nodeCount}:{currentNode}'] = round(float(re.findall(regex_rinaperf_rr ,rina.run('rinaperf', '-d', 'n.DIF', '-c', rrTransactions, '-t', 'rr', netns=f'node{currentNode}', stdout=subprocess.PIPE))[0]) * pow(10, -6), 4)

        #IP
        raw_redundant_ping_result_ip = re.search(regex_ping_raw, rina.run('ping', '10.0.0.1', '-q', '-c', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        redundant_ping_result_ip[f'{nodeCount}:{currentNode}'] = list(map(float, re.findall(regex_ping, raw_redundant_ping_result_ip)))
        redundant_ping_result_ip_min[f'{nodeCount}:{currentNode}'] = redundant_ping_result_ip[f'{nodeCount}:{currentNode}'][0]
        redundant_ping_result_ip_avg[f'{nodeCount}:{currentNode}'] = redundant_ping_result_ip[f'{nodeCount}:{currentNode}'][1]
        redundant_ping_result_ip_max[f'{nodeCount}:{currentNode}'] = redundant_ping_result_ip[f'{nodeCount}:{currentNode}'][2]
        redundant_ping_result_ip_mdev[f'{nodeCount}:{currentNode}'] = redundant_ping_result_ip[f'{nodeCount}:{currentNode}'][3]
        redundant_rr_tcp_result[f'{nodeCount}:{currentNode}'] = round(float(re.search(regex_netperf_rr, rina.run('netperf', '-H', '10.0.0.1', '-P', '0' '-t', 'TCP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)) * pow(10, -3), 4)
        redundant_rr_udp_result[f'{nodeCount}:{currentNode}'] = round(float(re.search(regex_netperf_rr, rina.run('netperf', '-H', '10.0.0.1', '-P', '0' '-t', 'UDP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)) * pow(10, -3), 4)
    
    return (plot(redundant_ping_result_rina_min,
    redundant_ping_result_rina_avg,
    redundant_ping_result_rina_max,
    redundant_ping_result_rina_mdev, 
    redundant_rr_result_rina, 
    redundant_ping_result_ip_min,
    redundant_ping_result_ip_avg,
    redundant_ping_result_ip_max,
    redundant_ping_result_ip_mdev,  
    redundant_rr_tcp_result, 
    redundant_rr_udp_result, 
    f'latency redundant path topology'))

def fully_meshed_latency_test():
    global nodeCount

    fully_meshed_ping_result_rina = {}
    fully_meshed_ping_result_rina_min = {}
    fully_meshed_ping_result_rina_avg = {}
    fully_meshed_ping_result_rina_max = {}
    fully_meshed_ping_result_rina_mdev = {}
    fully_meshed_rr_result_rina = {}
    fully_meshed_ping_result_ip = {}
    fully_meshed_ping_result_ip_min = {}
    fully_meshed_ping_result_ip_avg = {}
    fully_meshed_ping_result_ip_max = {}
    fully_meshed_ping_result_ip_mdev = {}
    fully_meshed_rr_tcp_result = {}
    fully_meshed_rr_udp_result = {}

    lo.info(f"Running latency test with fully meshed topology with {nodeCount} nodes.")

    rina.create_networknamespaces(nodeCount)
    rina.create_fully_meshed_topology(nodeCount)
    time.sleep(nodeCount)

    rina.run('bash', '-c', 'rinaperf -l -d n.DIF &', netns='node0')
    rina.run('netserver', netns='node0')

    for currentNode in range(nodeCount):
        #RINA
        raw_fully_meshed_ping_result_rina = re.search(regex_ping_raw, rina.run('rinaperf', '-d', 'n.DIF', 'ping','-D', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        fully_meshed_ping_result_rina[f'{nodeCount}:{currentNode}'] = list(map(float, re.findall(regex_ping, raw_fully_meshed_ping_result_rina)))
        fully_meshed_ping_result_rina_min[f'{nodeCount}:{currentNode}'] = fully_meshed_ping_result_rina[f'{nodeCount}:{currentNode}'][0]
        fully_meshed_ping_result_rina_avg[f'{nodeCount}:{currentNode}'] = fully_meshed_ping_result_rina[f'{nodeCount}:{currentNode}'][1]
        fully_meshed_ping_result_rina_max[f'{nodeCount}:{currentNode}'] = fully_meshed_ping_result_rina[f'{nodeCount}:{currentNode}'][2]
        fully_meshed_ping_result_rina_mdev[f'{nodeCount}:{currentNode}'] = fully_meshed_ping_result_rina[f'{nodeCount}:{currentNode}'][3]
        fully_meshed_rr_result_rina[f'{nodeCount}:{currentNode}'] = round(float(re.findall(regex_rinaperf_rr ,rina.run('rinaperf', '-d', 'n.DIF', '-c', rrTransactions, '-t', 'rr', netns=f'node{currentNode}', stdout=subprocess.PIPE))[0]) * pow(10, -6), 4)
    
        #IP
        raw_fully_meshed_ping_result_ip = re.search(regex_ping_raw, rina.run('ping', f'10.0.1.1', '-q', '-c', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        fully_meshed_ping_result_ip[f'{nodeCount}:{currentNode}'] = list(map(float, re.findall(regex_ping, raw_fully_meshed_ping_result_ip)))
        fully_meshed_ping_result_ip_min[f'{nodeCount}:{currentNode}'] = fully_meshed_ping_result_ip[f'{nodeCount}:{currentNode}'][0]
        fully_meshed_ping_result_ip_avg[f'{nodeCount}:{currentNode}'] = fully_meshed_ping_result_ip[f'{nodeCount}:{currentNode}'][1]
        fully_meshed_ping_result_ip_max[f'{nodeCount}:{currentNode}'] = fully_meshed_ping_result_ip[f'{nodeCount}:{currentNode}'][2]
        fully_meshed_ping_result_ip_mdev[f'{nodeCount}:{currentNode}'] = fully_meshed_ping_result_ip[f'{nodeCount}:{currentNode}'][3]
        fully_meshed_rr_tcp_result[f'{nodeCount}:{currentNode}'] = round(float(re.search(regex_netperf_rr, rina.run('netperf', '-H', '10.0.1.1', '-P', '0' '-t', 'TCP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)) * pow(10, -3), 4)
        fully_meshed_rr_udp_result[f'{nodeCount}:{currentNode}'] = round(float(re.search(regex_netperf_rr, rina.run('netperf', '-H', '10.0.1.1', '-P', '0' '-t', 'UDP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)) * pow(10, -3), 4)

    return (plot(fully_meshed_ping_result_rina_min,
    fully_meshed_ping_result_rina_avg,
    fully_meshed_ping_result_rina_max,
    fully_meshed_ping_result_rina_mdev,
    fully_meshed_rr_result_rina,
    fully_meshed_ping_result_ip_min,
    fully_meshed_ping_result_ip_avg,
    fully_meshed_ping_result_ip_max,
    fully_meshed_ping_result_ip_mdev,
    fully_meshed_rr_tcp_result, 
    fully_meshed_rr_udp_result, 
    f'Latency fully meshed topology'))

def main(args):    
    global LINE_SIZES, REDUNDANT_SIZES, MESH_SIZES
    LINE_SIZES = args.nodes
    REDUNDANT_SIZES = args.nodes
    MESH_SIZES = args.nodes

    test_results = []
    rina.load_rlite()

    global nodeCount

    for n in LINE_SIZES:
        rina.cleanup()
        nodeCount = n
        test_results += line_latency_test()
    for n in REDUNDANT_SIZES:
        rina.cleanup()
        nodeCount = n
        test_results += redundant_latency_test()
    for n in MESH_SIZES:
        rina.cleanup()
        nodeCount = n
        test_results += fully_meshed_latency_test()

    rina.cleanup()
    
    print(f'{test_results}')

    return test_results


if __name__ == "__main__":
    main()