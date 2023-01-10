#!/usr/bin/python3

import subprocess
import rina
import logging
import time
import re
import matplotlib.pyplot as plt

lo = logging.getLogger("rina")

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
            

# Line
line_result_rina = {}
line_result_ip = {}

rinaper_re = re.compile(r"Sender\s*\d*\s*[\d\.]*\s*([\d\.]*)")

def line_datarate_test():
    global line_result_rina
    global line_result_ip

    test_sizes = [2, 5]
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
        rina.run('netserver', netns='node0')
        while package_loss <= 10:
            rina.run('tc', 'qdisc', 'change', 'dev', f'veth{size - 1}-{size - 2}', 'root', 'netem', 'loss', str(package_loss)+'%', netns=f'node{size - 1}')
           
            try:
                rina_result_raw = rina.run('rinaperf', '-d', 'n.DIF', '-t', 'perf', '-s', '1460', '-D', '10', netns=f'node{size - 1}', stdout=subprocess.PIPE)
            except RuntimeError as e:
                print(f"rinaperf failed: {e}")
                rina_result_raw = ""

            match = re.search(rinaper_re, rina_result_raw)

            if match is None:
                print(f"No valid result from rinaperf: {rina_result_raw}")
                line_result_rina[f'{size}:{package_loss}'] = 0
            else:
                line_result_rina[f'{size}:{package_loss}'] = float(match.group(1))

            
            ip_result_raw =  rina.run('netperf', '-H', '10.0.0.1', '-P', '0', '--', '-o', 'THROUGHPUT', '--', '-m', '1460', netns=f'node{size - 1}', stdout=subprocess.PIPE)
            line_result_ip[f'{size}:{package_loss}'] = float(ip_result_raw.strip())
            package_loss += 0.5
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

            try:
                rina_result_raw = rina.run('rinaperf', '-d', 'n.DIF', '-t', 'perf', '-s', '1460', '-D', '10', netns=f'node{size - 1}', stdout=subprocess.PIPE)
            except RuntimeError as e:
                print(f"rinaperf failed: {e}")
                rina_result_raw = ""

            match = re.search(rinaper_re, rina_result_raw)

            if match is None:
                print(f"No valid result from rinaperf: {rina_result_raw}")
                mesh_result_rina[f'{size}:{package_loss}'] = 0
            else:
                mesh_result_rina[f'{size}:{package_loss}'] = float(match.group(1))

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

            try:
                rina_result_raw = rina.run('rinaperf', '-d', 'n.DIF', '-t', 'perf', '-s', '1460', '-D', '10', netns=f'node{size - 1}', stdout=subprocess.PIPE)
            except RuntimeError as e:
                print(f"rinaperf failed: {e}")
                rina_result_raw = ""

            match = re.search(rinaper_re, rina_result_raw)

            if match is None:
                print(f"No valid result from rinaperf: {rina_result_raw}")
                redundant_result_rina[f'{size}:{package_loss}'] = 0
            else:
                redundant_result_rina[f'{size}:{package_loss}'] = float(match.group(1))

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