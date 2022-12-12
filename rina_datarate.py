#!/usr/bin/python3

import subprocess
import rina
import logging
import time

lo = logging.getLogger("rina")

# Line
line_result_rina = {}
line_result_ip = {}


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
        line_result_rina[size] = rina.run('rinaperf', '-d', 'n.DIF', '-t', 'perf', netns=f'node{size - 1}', stdout=subprocess.PIPE)

        rina.run('netserver', netns='node0')
        line_result_ip[size] = rina.run('netperf', '-H', '10.0.0.1', netns=f'node{size - 1}', stdout=subprocess.PIPE)

    print(line_result_rina)
    print(line_result_ip)


def main():
    rina.load_rlite()
    line_datarate_test()
    rina.cleanup()


if __name__ == "__main__":
    main()