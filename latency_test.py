#!/usr/bin/python3

import subprocess
import rina
import logging
import time
import re
import pickle

lo = logging.getLogger("rina")

nodeCount = 3
nodeCountList = [5, 10, 20, 40, 65]
pingCount = 10
rrTransactions = 100

regex_ping_raw = re.compile('([0-9]+\.[0-9]+/){3}[0-9]+\.[0-9]+')
regex_ping = re.compile('[\d.]+')
regex_rinaperf_rr = re.compile('Sender\s*\d*\s*[\d\.]*\s*[\d\.]*\s*([\d]*)')
regex_netperf_rr = re.compile('[0-9\.]*')

###arrays line_latency_test###
#RINA
line_ping_result_rina = [None]*nodeCount
line_rr_result_rina = [None]*nodeCount
#IP
line_ping_result_ip = [None]*nodeCount
line_rr_tcp_result = [None]*nodeCount
line_rr_udp_result = [None]*nodeCount

###arrays redundant_latency_test###
#RINA
redundant_ping_result_rina = [None]*nodeCount
redundant_rr_result_rina = [None]*nodeCount
#IP
redundant_ping_result_ip = [None]*nodeCount
redundant_rr_tcp_result = [None]*nodeCount
redundant_rr_udp_result = [None]*nodeCount

###arrays fully_meshed_latency_test###
#RINA
fully_meshed_ping_result_rina = [None]*nodeCount
fully_meshed_rr_result_rina = [None]*nodeCount
#IP
fully_meshed_ping_result_ip = [None]*nodeCount
fully_meshed_rr_tcp_result = [None]*nodeCount
fully_meshed_rr_udp_result = [None]*nodeCount


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
        raw_line_ping_result_rina = re.search(regex_ping_raw, rina.run('rinaperf', '-d', 'n.DIF', 'ping','-D', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        line_ping_result_rina[currentNode] = list(map(float, re.findall(regex_ping, raw_line_ping_result_rina)))
        line_rr_result_rina[currentNode] = float(re.findall(regex_rinaperf_rr ,rina.run('rinaperf', '-d', 'n.DIF', '-c', rrTransactions, '-t', 'rr', netns=f'node{currentNode}', stdout=subprocess.PIPE))[0])
        
        #IP
        raw_line_ping_result_ip = re.search(regex_ping_raw, rina.run('ping', '10.0.0.1', '-q', '-c', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        line_ping_result_ip[currentNode] = list(map(float, re.findall(regex_ping, raw_line_ping_result_ip)))
        line_rr_tcp_result[currentNode] = float(re.search(regex_netperf_rr, rina.run('netperf', '-H', '10.0.0.1', '-P', '0' '-t', 'TCP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0))
        line_rr_udp_result[currentNode] = float(re.search(regex_netperf_rr, rina.run('netperf', '-H', '10.0.0.1', '-P', '0' '-t', 'UDP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0))

    with open("line_ping_result_rina", 'wb') as outfile:
        pickle.dump(line_ping_result_rina, outfile)
    with open("line_rr_result_rina", 'wb') as outfile:
        pickle.dump(line_rr_result_rina, outfile)
    
    with open("line_ping_result_ip", 'wb') as outfile:
        pickle.dump(line_ping_result_ip, outfile)
    with open("line_rr_tcp_result", 'wb') as outfile:
        pickle.dump(line_rr_tcp_result, outfile)
    with open("line_rr_udp_result", 'wb') as outfile:
        pickle.dump(line_rr_udp_result, outfile)

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
        raw_redundant_ping_result_rina = re.search(regex_ping_raw, rina.run('rinaperf', '-d', 'n.DIF', 'ping','-D', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        redundant_ping_result_rina[currentNode] = list(map(float, re.findall(regex_ping, raw_redundant_ping_result_rina)))
        redundant_rr_result_rina[currentNode] = float(re.findall(regex_rinaperf_rr ,rina.run('rinaperf', '-d', 'n.DIF', '-c', rrTransactions, '-t', 'rr', netns=f'node{currentNode}', stdout=subprocess.PIPE))[0])
        
        #IP
        raw_redundant_ping_result_ip = re.search(regex_ping_raw, rina.run('ping', '10.0.0.1', '-q', '-c', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        redundant_ping_result_ip[currentNode] = list(map(float, re.findall(regex_ping, raw_redundant_ping_result_ip)))
        redundant_rr_tcp_result[currentNode] = float(re.search(regex_netperf_rr, rina.run('netperf', '-H', '10.0.0.1', '-P', '0' '-t', 'TCP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0))
        redundant_rr_udp_result[currentNode] = float(re.search(regex_netperf_rr, rina.run('netperf', '-H', '10.0.0.1', '-P', '0' '-t', 'UDP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0))

    with open("redundant_ping_result_rina", 'wb') as outfile:
        pickle.dump(redundant_ping_result_rina, outfile)
    with open("redundant_rr_result_rina", 'wb') as outfile:
        pickle.dump(redundant_rr_result_rina, outfile)
    
    with open("redundant_ping_result_ip", 'wb') as outfile:
        pickle.dump(redundant_ping_result_ip, outfile)
    with open("redundant_rr_tcp_result", 'wb') as outfile:
        pickle.dump(redundant_rr_tcp_result, outfile)
    with open("redundant_rr_udp_result", 'wb') as outfile:
        pickle.dump(redundant_rr_udp_result, outfile)

def fully_meshed_latency_test():
    lo.info(f"Running latency test with fully meshed topology with {nodeCount} nodes.")

    global fully_meshed_ping_result_rina
    global fully_meshed_rr_result_rina
    global fully_meshed_ping_result_ip
    global fully_meshed_rr_tcp_result
    global fully_meshed_rr_udp_result

    rina.create_networknamespaces(nodeCount)
    rina.create_fully_meshed_topology(nodeCount)
    time.sleep(nodeCount/2)

    rina.run('bash', '-c', 'rinaperf -l -d n.DIF &', netns='node0')
    rina.run('netserver', netns='node0')

    for currentNode in range(nodeCount):
        #RINA
        raw_fully_meshed_ping_result_rina = re.search(regex_ping_raw, rina.run('rinaperf', '-d', 'n.DIF', 'ping','-D', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        fully_meshed_ping_result_rina[currentNode] = list(map(float, re.findall(regex_ping, raw_fully_meshed_ping_result_rina)))
        fully_meshed_rr_result_rina[currentNode] = float(re.findall(regex_rinaperf_rr ,rina.run('rinaperf', '-d', 'n.DIF', '-c', rrTransactions, '-t', 'rr', netns=f'node{currentNode}', stdout=subprocess.PIPE))[0])
        
        #IP
        raw_fully_meshed_ping_result_ip = re.search(regex_ping_raw, rina.run('ping', f'10.0.1.1', '-q', '-c', pingCount, netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0)
        fully_meshed_ping_result_ip[currentNode] = list(map(float, re.findall(regex_ping, raw_fully_meshed_ping_result_ip)))
        fully_meshed_rr_tcp_result[currentNode] = float(re.search(regex_netperf_rr, rina.run('netperf', '-H', '10.0.1.1', '-P', '0' '-t', 'TCP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0))
        fully_meshed_rr_udp_result[currentNode] = float(re.search(regex_netperf_rr, rina.run('netperf', '-H', '10.0.1.1', '-P', '0' '-t', 'UDP_RR', '-l', '-'+str(rrTransactions), '--', '-o', 'mean_latency', netns=f'node{currentNode}', stdout=subprocess.PIPE)).group(0))

    with open("fully_meshed_ping_result_rina", 'wb') as outfile:
        pickle.dump(fully_meshed_ping_result_rina, outfile)
    with open("fully_meshed_rr_result_rina", 'wb') as outfile:
        pickle.dump(fully_meshed_rr_result_rina, outfile)
    
    with open("fully_meshed_ping_result_ip", 'wb') as outfile:
        pickle.dump(fully_meshed_ping_result_ip, outfile)
    with open("fully_meshed_rr_tcp_result", 'wb') as outfile:
        pickle.dump(fully_meshed_rr_tcp_result, outfile)
    with open("fully_meshed_rr_udp_result", 'wb') as outfile:
        pickle.dump(fully_meshed_rr_udp_result, outfile)


def main():
    rina.load_rlite()
    #rina.cleanup()
    #line_latency_test()
    #rina.cleanup()
    #redundant_latency_test()
    rina.cleanup()
    fully_meshed_latency_test()
    rina.cleanup()

    print("Results")
    print("Line")
    print(f"Ping RINA in ms: {line_ping_result_rina}")
    print(f"Ping IP in ms: {line_ping_result_ip}")
    print(f"RR RINA: {line_rr_result_rina}")
    print(f"RR TCP: {line_rr_tcp_result}")
    print(f"RR UDP: {line_rr_udp_result}")
    print(f"\n")
    print("------------------------------------------------------------------")
    print(f"\n")
    print("Redundant")
    print(f"Ping RINA: {redundant_ping_result_rina}")
    print(f"Ping IP: {redundant_ping_result_ip}")
    print(f"RR RINA: {redundant_rr_result_rina}")
    print(f"RR TCP: {redundant_rr_tcp_result}")
    print(f"RR UDP: {redundant_rr_udp_result}")
    print(f"\n")
    print("------------------------------------------------------------------")
    print(f"\n")
    print("Fully meshed")
    print(f"Ping RINA: {fully_meshed_ping_result_rina}")
    print(f"Ping IP: {fully_meshed_ping_result_ip}")
    print(f"RR RINA: {fully_meshed_rr_result_rina}")
    print(f"RR TCP: {fully_meshed_rr_tcp_result}")
    print(f"RR UDP: {fully_meshed_rr_udp_result}")


if __name__ == "__main__":
    main()