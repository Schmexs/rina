#!/usr/bin/python3

import rina
import logging
import time
import re
import datarate

lo = logging.getLogger("rina")
rinaper_re = re.compile(r"Receiver\s*\d*\s*[\d\.]*\s*([\d\.]*)")

def plot(result_rina: dict, result_ip: dict, title: str) -> dict:
    series_ip = {
        'name': f'IP',
        'data': [[size, res] for size, res in result_ip.items()],
        'dashed': True
    }

    series_rina = {
        'name': f'RINA',
        'data': [[size, res] for size, res in result_rina.items()],
        'dashed': False
    }

    series = [series_rina, series_ip]

    return {title:series} 

def match_rina_result(result):
    return float(re.search(rinaper_re, result).group(1))
            

# Line
line_result_rina = {}
line_result_ip = {}

def line_datarate_test():
    global line_result_rina
    global line_result_ip

    #test_sizes = [2, 5]
    test_sizes = [2, 5, 10, 30]

    for size in test_sizes:
        lo.info(f"Running datarate test with line topology with {size} nodes.")
        rina.cleanup()
        rina.create_networknamespaces(size)
        rina.create_line_topology(size)
        time.sleep(size)
       
        result_ip, result_rina = datarate.datarate_test(f'node{size - 1}', 'node0', '10.0.0.1')          

        line_result_ip[size] = result_ip
        line_result_rina[size] = result_rina

        print(f"RESULT IP: {result_ip}")
        print(f"RESULT RINA: {result_rina}")


    return (plot(line_result_rina, line_result_ip, 'Datarate Line topology'))


# Fully meshed
mesh_result_rina = {}
mesh_result_ip = {}

def mesh_datarate_test():
    global mesh_result_rina
    global mesh_result_ip

    #test_sizes = [3, 6]
    test_sizes = [5, 10, 30]

    for size in test_sizes:
        lo.info(f"Running datarate test with fully meshed topology with {size} nodes.")

        rina.cleanup()
        rina.create_networknamespaces(size)
        rina.create_fully_meshed_topology(size)
        time.sleep(size * 3)

        result_ip, result_rina = datarate.datarate_test(f'node{size - 1}', 'node0', f'10.0.{size-1}.1')          

        line_result_ip[size] = result_ip
        line_result_rina[size] = result_rina

        print(f"RESULT IP: {result_ip}")
        print(f"RESULT RINA: {result_rina}")

    return(plot(mesh_result_rina, mesh_result_ip, 'Datarate fully meshed topology'))


# Redundant
redundant_result_rina = {}
redundant_result_ip = {}

def redundant_datarate_test():
    global redundant_result_rina
    global redundant_result_ip

    #test_sizes = [8]
    test_sizes = [5, 10, 30]

    for size in test_sizes:
        lo.info(f"Running datarate test with Redundant topology with {size} nodes.")

        rina.cleanup()
        rina.create_networknamespaces(size)
        rina.create_redundant_paths_topology(size)
        time.sleep(size * 5)

        result_ip, result_rina = datarate.datarate_test(f'node{size - 1}', 'node0', f'10.0.0.1'   )          

        line_result_ip[size] = result_ip
        line_result_rina[size] = result_rina

        print(f"RESULT IP: {result_ip}")
        print(f"RESULT RINA: {result_rina}")

    return(plot(redundant_result_rina, redundant_result_ip, 'Datarate redundant topology'))


def main() -> list:
    test_results = []
    rina.load_rlite()
    test_results.append(line_datarate_test())
    test_results.append(mesh_datarate_test())
    test_results.append(redundant_datarate_test())
    rina.cleanup()

    return test_results

if __name__ == '__main__':
    main()