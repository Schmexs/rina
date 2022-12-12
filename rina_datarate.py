#!/usr/bin/python3

import subprocess
import rina
import logging
import time
import re

lo = logging.getLogger("rina")

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
        rina.cleanup()
        rina.create_networknamespaces(size)
        rina.create_line_topology(size)
        time.sleep(size/2)

        rina.run('bash', '-c', 'rinaperf -l -d n.DIF &', netns='node0')
        rina_result_raw = rina.run('rinaperf', '-d', 'n.DIF', '-t', 'perf', netns=f'node{size - 1}', stdout=subprocess.PIPE)

        match = re.search(rinaper_re, rina_result_raw)

        if match is None:
            raise ValueError(f"No valid result from rinaperf: {rina_result_raw}")

        line_result_rina[size] = float(match.group(1))

        rina.run('netserver', netns='node0')
        ip_result_raw =  rina.run('netperf', '-H', '10.0.0.1', '-P', '0', '--', '-o', 'THROUGHPUT', netns=f'node{size - 1}', stdout=subprocess.PIPE)
        line_result_ip[size] = float(ip_result_raw.strip())

    print(line_result_rina)
    print(line_result_ip)


def main():
    rina.load_rlite()
    line_datarate_test()
    rina.cleanup()


if __name__ == "__main__":
    main()