#!/usr/bin/python3

import subprocess
import rina
import logging
import time
import re
import matplotlib.pyplot as plt
import statistics
import json
import datarate

LOSS_START = 0.05
LOSS_INCREASE = 0.05
LOSS_MAX = 0.3
LINE_SIZES = [2, 5, 15]
MESH_SIZES = [5, 15]
REDUNDANT_SIZES = [10]

lo = logging.getLogger("rina")
lo.setLevel(logging.DEBUG)
rinaper_re = re.compile(r"Receiver\s*\d*\s*[\d\.]*\s*([\d\.]*)")

def plot(result_rina, result_ip, title) -> dict:
    series = []
    size = []
    loss = []
  
    for key in result_rina:
        s = int(key.split(':')[0])
        l = float(key.split(':')[1])
        size.append(s) if s not in size else None
        loss.append(l) if l not in loss else None
    
    all_rina_series = []
    all_ip_series = []

    for s in size:
        x = []
        y = []
        y2 = []
        for l in loss:
            x.append(l)
            y.append(result_rina[f'{s}:{l}'])
            y2.append(result_ip[f'{s}:{l}'])

        rina_series = {
            'name': f'{s}-nodes - RINA',
            'data': list((x[i], y[i]) for i in range(len(x))),
            'dashed': False
        }
        
        ip_series = {
            'name': f'{s}-nodes - IP',
            'data': list((x[i], y2[i]) for i in range(len(x))),
            'dashed': True
        }
        all_rina_series.append(rina_series)
        all_ip_series.append(ip_series)  

    series = all_rina_series + all_ip_series

    return {title:series} 

def match_rina_result(result):
    return float(re.search(rinaper_re, result).group(1))
            

# Line
line_result_rina = {}
line_result_ip = {}

def line_datarate_test(args):
    global line_result_rina
    global line_result_ip

    for size in LINE_SIZES:
        lo.info(f"Running datarate test with line topology with {size} nodes.")
        rina.cleanup()
        rina.create_networknamespaces(size)
        rina.create_line_topology(size)
        time.sleep(size)
        package_loss = LOSS_START
        rina.run('tc', 'qdisc', 'add', 'dev', f'veth{size - 1}-{size - 2}', 'root', 'netem', 'loss', str(package_loss)+'%', netns=f'node{size - 1}')
    
        while package_loss <= LOSS_MAX:
            rina.run('tc', 'qdisc', 'change', 'dev', f'veth{size - 1}-{size - 2}', 'root', 'netem', 'loss', str(package_loss)+'%', netns=f'node{size - 1}')
           
            result_ip, result_rina = datarate.datarate_test(f'node{size - 1}', 'node0', '10.0.0.1', args=args)          

            line_result_ip[f'{size}:{package_loss}'] = result_ip
            line_result_rina[f'{size}:{package_loss}'] = result_rina

            #print(f"RESULT IP: {line_result_ip[f'{size}:{package_loss}']}")
            #print(f"RESULT RINA: {line_result_rina[f'{size}:{package_loss}']}")

            package_loss += LOSS_INCREASE

    return (plot(line_result_rina, line_result_ip, 'Packet loss Line topology'))


line_reno_result_ip = {}

def line_datarate_reno_test(args):
    global line_reno_result_ip

    for size in LINE_SIZES:
        lo.info(f"Running datarate RENO test with line topology with {size} nodes.")
        rina.cleanup()
        rina.create_networknamespaces(size)
        rina.create_line_topology(size)
        time.sleep(size)
        package_loss = LOSS_START
        rina.run('tc', 'qdisc', 'add', 'dev', f'veth{size - 1}-{size - 2}', 'root', 'netem', 'loss', str(package_loss)+'%', netns=f'node{size - 1}')
    
        while package_loss <= LOSS_MAX:
            rina.run('tc', 'qdisc', 'change', 'dev', f'veth{size - 1}-{size - 2}', 'root', 'netem', 'loss', str(package_loss)+'%', netns=f'node{size - 1}')
           
            result_ip, _ = datarate.datarate_test(f'node{size - 1}', 'node0', '10.0.0.1', tcp_congestion_algo='reno', skip_rina=True, args=args)          

            line_reno_result_ip[f'{size}:{package_loss}'] = result_ip

            #print(f"RESULT IP: {line_result_ip[f'{size}:{package_loss}']}")
            #print(f"RESULT RINA: {line_result_rina[f'{size}:{package_loss}']}")

            package_loss += LOSS_INCREASE

    return (plot(line_result_rina, line_reno_result_ip, 'Packet loss Line topology RENO'))


# Fully meshed
mesh_result_rina = {}
mesh_result_ip = {}

def mesh_datarate_test(args):
    global mesh_result_rina
    global mesh_result_ip

    for size in MESH_SIZES:
        lo.info(f"Running datarate test with fully meshed topology with {size} nodes.")

        rina.cleanup()
        rina.create_networknamespaces(size)
        rina.create_fully_meshed_topology(size)
        time.sleep(size * 3)
        package_loss = LOSS_START

        for i in range(size - 1):
            rina.run('tc', 'qdisc', 'add', 'dev', f'veth{size - 1}-{i}', 'root','netem', 'loss', str(package_loss)+'%', netns=f'node{size - 1}')
        
        while package_loss <= LOSS_MAX:
            for i in range(size - 1):
                rina.run('tc', 'qdisc', 'change', 'dev', f'veth{size - 1}-{i}', 'root','netem', 'loss', str(package_loss)+'%', netns=f'node{size - 1}')

            result_ip, result_rina = datarate.datarate_test(f'node{size - 1}', 'node0', f'10.0.{size-1}.1', args=args)          

            line_result_ip[f'{size}:{package_loss}'] = result_ip
            line_result_rina[f'{size}:{package_loss}'] = result_rina

            #print(f"RESULT IP: {mesh_result_ip[f'{size}:{package_loss}']}")
            #print(f"RESULT RINA: {mesh_result_rina[f'{size}:{package_loss}']}")

            package_loss += LOSS_INCREASE

    return(plot(mesh_result_rina, mesh_result_ip, 'Packet loss fully meshed topology'))


# Redundant
redundant_result_rina = {}
redundant_result_ip = {}

def redundant_datarate_test(args):
    global redundant_result_rina
    global redundant_result_ip

    for size in REDUNDANT_SIZES:
        lo.info(f"Running datarate test with Redundant topology with {size} nodes.")

        rina.cleanup()
        rina.create_networknamespaces(size)
        rina.create_redundant_paths_topology(size)
        time.sleep(size * 5)
        package_loss = LOSS_START
        
        if size >= 4:
            if size % 3 == 0:
                neighbors = [size-2, size-3, size-4]
            elif size % 3 == 2:
                neighbors = [size-2, size-4]
            elif size % 3 == 1:
                neighbors = [size-4]
            else:
                neighbors = []
        else:
            neighbors = []
        
        for n in neighbors:
            rina.run('tc', 'qdisc', 'add', 'dev', f'veth{size-1}-{n}', 'root', 'netem', 'loss', str(package_loss)+'%', netns=f'node{size-1}')

        while package_loss <= LOSS_MAX:
            for n in neighbors:
                rina.run('tc', 'qdisc', 'change', 'dev', f'veth{size-1}-{n}', 'root', 'netem', 'loss', str(package_loss)+'%', netns=f'node{size-1}')
            
            result_ip, result_rina = datarate.datarate_test(f'node{size - 1}', 'node0', f'10.0.0.1', args=args)          

            line_result_ip[f'{size}:{package_loss}'] = result_ip
            line_result_rina[f'{size}:{package_loss}'] = result_rina

            #print(f"RESULT IP: {redundant_result_ip[f'{size}:{package_loss}']}")
            #print(f"RESULT RINA: {redundant_result_rina[f'{size}:{package_loss}']}")

            package_loss += LOSS_INCREASE

    return(plot(redundant_result_rina, redundant_result_ip, 'Packet loss redundant topology'))


def main(args) -> list:
    global LINE_SIZES, REDUNDANT_SIZES, MESH_SIZES, LOSS_START, LOSS_INCREASE, LOSS_MAX
    LINE_SIZES = args.nodes
    REDUNDANT_SIZES = args.nodes
    MESH_SIZES = args.nodes
    LOSS_START = args.loss_start
    LOSS_INCREASE = args.loss_increase
    LOSS_MAX = args.loss_max

    test_results = []
    rina.load_rlite()
    test_results.append(line_datarate_test(args))
    test_results.append(line_datarate_reno_test(args))
    #test_results.append(mesh_datarate_test())
    test_results.append(redundant_datarate_test(args))
    rina.cleanup()

    return test_results

if __name__ == '__main__':
    main()