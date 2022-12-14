#!/usr/bin/python3

import subprocess
import rina
import logging
import time
import re

lo = logging.getLogger("rina")

nodeCount = 3
pingCount = 10
rrTransactions = 100

regex_ping = re.compile('([0-9]+\.[0-9]+/){3}[0-9]+\.[0-9]+')
regex_rinaperf_rr = re.compile('Sender\s*\d*\s*[\d\.]*\s*[\d\.]*\s*([\d]*)')
regex_netperf_rr = re.compile('[0-9\.]*')

###arrays line_latency_test###
#RINA
line_ping_result_rina = {}
line_rr_result_rina = {}
#IP
line_ping_result_ip = {}
line_rr_tcp_result = {}
line_rr_udp_result = {}

###arrays redundant_latency_test###
#RINA
redundant_ping_result_rina = {}
redundant_rr_result_rina = {}
#IP
redundant_ping_result_ip = {}
redundant_rr_tcp_result = {}
redundant_rr_udp_result = {}

def line_latency_test():
    lo.info(f"Running latency test with line topology with {nodeCount} nodes.")

    global line_ping_result_rina
    global line_rr_result_rina
    global line_ping_result_ip
    global line_rr_tcp_result 
    global line_rr_udp_result 

    rina.create_networknamespaces(nodeCount)
    rina.create_line_topology(nodeCount)
    time.sleep(nodeCount/2)

    rina.run('bash', '-c', 'rinaperf -l -d n.DIF &', netns='node0')
    rina.run('netserver', netns='node0')
    
    for currentNode in range(nodeCount):
        #RINA
        line_ping_result_rina[currentNode] = re.search(regex_ping, rina.run('rinaperf', '-d', 'n.DIF', 'ping','-D', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        line_rr_result_rina[currentNode] = re.findall(regex_rinaperf_rr ,rina.run('rinaperf', '-d', 'n.DIF', '-c', rrTransactions, '-t', 'rr', netns=f'node{currentNode}', stdout=subprocess.PIPE))[0]
        
        #IP
        line_ping_result_ip[currentNode] = re.search(regex_ping, rina.run('ping', '10.0.0.1', '-q', '-c', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        line_rr_tcp_result[currentNode] = re.search(regex_netperf_rr, rina.run('netperf', '-H', '10.0.0.1', '-P', '0' '-t', 'TCP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        line_rr_udp_result[currentNode] = re.search(regex_netperf_rr, rina.run('netperf', '-H', '10.0.0.1', '-P', '0' '-t', 'UDP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)

def redundant_latency_test():
    lo.info(f"Running latency test with redundant topology with {nodeCount} nodes.")

    global redundant_ping_result_rina
    global redundant_rr_result_rina
    global redundant_ping_result_ip
    global redundant_rr_tcp_result
    global redundant_rr_udp_result

    rina.create_networknamespaces(nodeCount)
    rina.create_redundant_paths_topology(nodeCount)
    time.sleep(nodeCount/2)

    rina.run('bash', '-c', 'rinaperf -l -d n.DIF &', netns='node0')
    rina.run('netserver', netns='node0')

    for currentNode in range(nodeCount):
        #RINA
        redundant_ping_result_rina[currentNode] = re.search(regex_ping, rina.run('rinaperf', '-d', 'n.DIF', 'ping','-D', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        redundant_rr_result_rina[currentNode] = re.findall(regex_rinaperf_rr ,rina.run('rinaperf', '-d', 'n.DIF', '-c', rrTransactions, '-t', 'rr', netns=f'node{currentNode}', stdout=subprocess.PIPE))[0]
        
        #IP
        redundant_ping_result_ip[currentNode] = re.search(regex_ping, rina.run('ping', '10.0.0.1', '-q', '-c', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        redundant_rr_tcp_result[currentNode] = re.search(regex_netperf_rr, rina.run('netperf', '-H', '10.0.0.1', '-P', '0' '-t', 'TCP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        redundant_rr_udp_result[currentNode] = re.search(regex_netperf_rr, rina.run('netperf', '-H', '10.0.0.1', '-P', '0' '-t', 'UDP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)

def main():
    rina.load_rlite()
    rina.cleanup()
    line_latency_test()
    rina.cleanup()
    redundant_latency_test()
    rina.cleanup()

    print(line_ping_result_rina)
    print(line_ping_result_ip)
    print(line_rr_result_rina)
    print(line_rr_tcp_result)
    print(line_rr_udp_result)

    print(redundant_ping_result_rina)
    print(redundant_ping_result_ip)
    print(redundant_rr_result_rina)
    print(redundant_rr_tcp_result)
    print(redundant_rr_udp_result)


if __name__ == "__main__":
    main()