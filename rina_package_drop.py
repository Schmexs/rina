#!/usr/bin/python3

import subprocess
import rina
import logging
import time
import re
import matplotlib.pyplot as plt
import statistics
import json

lo = logging.getLogger("rina")
rinaper_re = re.compile(r"Receiver\s*\d*\s*[\d\.]*\s*([\d\.]*)")

def plot(result_rina, result_ip, title):
    size = []
    loss = []
  
    for key in result_rina:
        s = int(key.split(':')[0])
        l = float(key.split(':')[1])
        size.append(s) if s not in size else None
        loss.append(l) if l not in loss else None
    
    for s in size:
        x = []
        y = []
        y2 = []
        for l in loss:
            x.append(l)
            y.append(result_rina[f'{s}:{l}'])
            y2.append(result_ip[f'{s}:{l}'])
        
        plt.plot(x, y, label=f'{s}-nodes')
        plt.plot(x, y2, linestyle='dashed', label=f'{s}-nodes')
        plt.title(title)
    
    plt.legend()
    plt.show()

def match_rina_result(result):
    return float(re.search(rinaper_re, result).group(1))
            

# Line
line_result_rina = {}
line_result_ip = {}


def line_datarate_test():
    global line_result_rina
    global line_result_ip

    test_sizes = [2]
    #test_sizes = [2, 5, 10, 30, 50]

    for size in test_sizes:
        lo.info(f"Running datarate test with line topology with {size} nodes.")
        rina.cleanup()
        rina.create_networknamespaces(size)
        rina.create_line_topology(size)
        time.sleep(size)
        package_loss = 0.5
        rina.run('tc', 'qdisc', 'add', 'dev', f'veth{size - 1}-{size - 2}', 'root', 'netem', 'loss', str(package_loss)+'%', netns=f'node{size - 1}')
        
        rina.run('bash', '-c', 'rinaperf -l -d n.DIF &', netns='node0')
        rina.run('bash', '-c', 'iperf3 -s &', netns='node0')
        while package_loss <= 6:
            rina.run('tc', 'qdisc', 'change', 'dev', f'veth{size - 1}-{size - 2}', 'root', 'netem', 'loss', str(package_loss)+'%', netns=f'node{size - 1}')
           
            results_rina = []
            results_ip = []

            for _ in range(3):
                try:
                    rina_result_raw = rina.run('rinaperf', '-d', 'n.DIF', '-t', 'perf', '-s', '1460', '-D', '5', netns=f'node{size - 1}', stdout=subprocess.PIPE)    
                    results_rina.append(match_rina_result(rina_result_raw))
                except RuntimeError as e:
                    print(f"rinaperf failed: {e}")
                    results_rina.append(0)

                
                try :
                    ip_result_raw =  rina.run('iperf3', '-c', '10.0.0.1','-J', '-t', '5', '-M', '1460', netns=f'node{size - 1}', stdout=subprocess.PIPE)
                    ip_result_dict = json.loads(ip_result_raw)
                    results_ip.append(ip_result_dict['end']["sum_received"]['bits_per_second'] / 10 ** 6)
                except (RuntimeError, KeyError) as e:
                    results_ip.append(0)
                    print(f"iperf3 failed: {e}")

                
            line_result_ip[f'{size}:{package_loss}'] = statistics.mean(results_ip)
            line_result_rina[f'{size}:{package_loss}'] = statistics.mean(results_rina)

            print(f"RESULT IP: {line_result_ip[f'{size}:{package_loss}']}")
            print(f"RESULT RINA: {line_result_rina[f'{size}:{package_loss}']}")

            package_loss += 2

    plot(line_result_rina, line_result_ip, "Line topology")

# Fully meshed
mesh_result_rina = {}
mesh_result_ip = {}

def mesh_datarate_test():
    global mesh_result_rina
    global mesh_result_ip

    test_sizes = [3, 6]
    #test_sizes = [2, 5, 10, 30, 50]

    for size in test_sizes:
        lo.info(f"Running datarate test with fully meshed topology with {size} nodes.")

        rina.cleanup()
        rina.create_networknamespaces(size)
        rina.create_fully_meshed_topology(size)
        time.sleep(size * 3)
        package_loss = 0.5

        for i in range(size - 1):
            rina.run('tc', 'qdisc', 'add', 'dev', f'veth{size - 1}-{i}', 'root','netem', 'loss', str(package_loss)+'%', netns=f'node{size - 1}')
        
        
        rina.run('bash', '-c', 'rinaperf -l -d n.DIF &', netns='node0')
        rina.run('netserver', netns='node0')

        while package_loss <= 10:
            for i in range(size - 1):
                rina.run('tc', 'qdisc', 'change', 'dev', f'veth{size - 1}-{i}', 'root','netem', 'loss', str(package_loss)+'%', netns=f'node{size - 1}')

            value = []
            for i in range(5):
                try:
                    rina_result_raw = rina.run('rinaperf', '-d', 'n.DIF', '-t', 'perf', '-s', '1460', '-D', '10', netns=f'node{size - 1}', stdout=subprocess.PIPE)
                    value.append(match_rina_result(rina_result_raw))
                except RuntimeError as e:
                    print(f"rinaperf failed: {e}")
                    rina_result_raw = ""

            result = statistics.mean(value)

            if result is None:
                print(f"No valid result from rinaperf: {result}")
                mesh_result_rina[f'{size}:{package_loss}'] = 0
            else:
                mesh_result_rina[f'{size}:{package_loss}'] = result

            ip_result_raw =  rina.run('netperf', '-H', f'10.0.{size-1}.1', '-P', '0', '--', '-o', 'THROUGHPUT', '--', '-m', '1460', netns=f'node{size - 1}', stdout=subprocess.PIPE)
            mesh_result_ip[f'{size}:{package_loss}'] = float(ip_result_raw.strip())
            package_loss += 0.5

    plot(mesh_result_rina, mesh_result_ip, "Mesh topology")


# Redundant
redundant_result_rina = {}
redundant_result_ip = {}

def redundant_datarate_test():
    global redundant_result_rina
    global redundant_result_ip

    test_sizes = [5, 6, 8]
    #test_sizes = [4, 5, 10, 30, 50]

    for size in test_sizes:
        lo.info(f"Running datarate test with Redundant topology with {size} nodes.")

        rina.cleanup()
        rina.create_networknamespaces(size)
        rina.create_redundant_paths_topology(size)
        time.sleep(size * 5)
        package_loss = 0.5
        
        if size % 3 == 0:
            neighbors = [size-2, size-3, size-4]
        elif size % 3 == 2:
            neighbors = [size-2, size-4]
        elif size % 3 == 1:
            neighbors = [size-4]
        else:
            neighbors = []
        
        for n in neighbors:
            rina.run('tc', 'qdisc', 'add', 'dev', f'veth{size-1}-{n}', 'root', 'netem', 'loss', str(package_loss)+'%', netns=f'node{size-1}')
        
        rina.run('bash', '-c', 'rinaperf -l -d n.DIF &', netns='node0')
        rina.run('netserver', netns='node0')

        while package_loss <= 10:
            for n in neighbors:
                rina.run('tc', 'qdisc', 'change', 'dev', f'veth{size-1}-{n}', 'root', 'netem', 'loss', str(package_loss)+'%', netns=f'node{size-1}')

            value = []
            for i in range(5):
                try:
                    rina_result_raw = rina.run('rinaperf', '-d', 'n.DIF', '-t', 'perf', '-s', '1460', '-D', '10', netns=f'node{size - 1}', stdout=subprocess.PIPE)
                    value.append(match_rina_result(rina_result_raw))
                except RuntimeError as e:
                    print(f"rinaperf failed: {e}")
                    rina_result_raw = ""

            result = statistics.mean(value)

            if result is None:
                print(f"No valid result from rinaperf: {result}")
                redundant_result_rina[f'{size}:{package_loss}'] = 0
            else:
                redundant_result_rina[f'{size}:{package_loss}'] = result

            ip_result_raw =  rina.run('netperf', '-H', '10.0.0.1', '-P', '0', '--', '-o', 'THROUGHPUT', '--', '-m', '1460', netns=f'node{size - 1}', stdout=subprocess.PIPE)
            redundant_result_ip[f'{size}:{package_loss}'] = float(ip_result_raw.strip())
            package_loss += 0.5

    plot(redundant_result_rina, redundant_result_ip, "Redundant topology")


def main():
    rina.load_rlite()
    line_datarate_test()
    mesh_datarate_test()
    redundant_datarate_test()
    rina.cleanup()

    print("RESULTS: (in MBit/s)")
    print("LINE")
    print(f"TCP/IP: {line_result_ip}")
    print(f"RINA: {line_result_rina}")
    print("\n")
    print("MESH:")
    print(f"TCP/IP: {mesh_result_ip}")
    print(f"RINA: {mesh_result_rina}")
    print("\n")
    print("REDUNDANT:")
    print(f"TCP/IP: {redundant_result_ip}")
    print(f"RINA: {redundant_result_rina}")


if __name__ == "__main__":
    main()