import json
import statistics
import rina
import subprocess
import re

SAMPLES = 4
RETIRES_MAX = 10

rinaper_re = re.compile(r"Receiver\s*\d*\s*[\d\.]*\s*([\d\.]*)")


def match_rina_result(result):
    return float(re.search(rinaper_re, result).group(1))

def datarate_test(from_ns, to_ns, to_ip, tcp_congestion_algo='cubic', skip_rina=False):
    rina.run('bash', '-c', 'rinaperf -l -d n.DIF &', netns=to_ns)
    rina.run('bash', '-c', 'iperf3 -s &', netns=to_ns)

    results_rina = []
    results_ip = []

    result_rina = None

    if not skip_rina:
        timeout_try_rina = 0
        success_try_rina = 0
        while success_try_rina < SAMPLES:
            if timeout_try_rina > RETIRES_MAX:
                results_rina.append(0)
                break
            try:
                rina_result_raw = rina.run('rinaperf', '-d', 'n.DIF', '-t', 'perf', '-s', '1460', '-D', '5', '-g', '0', netns=from_ns, stdout=subprocess.PIPE)
                results_rina.append(match_rina_result(rina_result_raw))
                success_try_rina += 1
            except RuntimeError as e:
                print(f"rinaperf failed: {e}")
                timeout_try_rina += 1
                #results_rina.append(0)
        
        result_rina = round(statistics.mean(results_rina))

    timeout_try_ip = 0
    success_try_ip = 0
    while success_try_ip < SAMPLES:
        if timeout_try_ip > RETIRES_MAX:
            results_ip.append(0)
            break
        try :
            ip_result_raw =  rina.run('iperf3', '-c', to_ip, '-J', '-t', '5', '-M', '1460', '-C', tcp_congestion_algo, netns=from_ns, stdout=subprocess.PIPE)
            ip_result_dict = json.loads(ip_result_raw)
            results_ip.append(ip_result_dict['end']["sum_received"]['bits_per_second'] / 10 ** 6)
            success_try_ip += 1
        except (RuntimeError, KeyError) as e:
            #results_ip.append(0)
            timeout_try_ip += 1
            print(f"iperf3 failed: {e}")

    result_ip = round(statistics.mean(results_ip))

    rina.run('killall', 'rinaperf', netns=to_ns)
    rina.run('killall', 'iperf3', netns=to_ns)

    return result_ip, result_rina


