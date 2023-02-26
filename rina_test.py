import json
import rina_package_drop as rpd
import rina_datarate as rd
import latency_test as rlt
import time
import argparse

def write_json(data):
    t = round(time.time())
    with open(f'data-{t}.json', 'w') as file:
        json.dump(data, file, indent=4)

def create_json(title, x_name, x_unit, y_name, y_unit, series):
    id = title.replace(" ", "_").lower()

    json = {
        "id": id,
        "title": title,
        "axes": {
            "x": {
                "name": x_name,
                "unit": x_unit
            },
            "y": {
                "name": y_name,
                "unit": y_unit
            }
        },
        "series": series
    }
    return json


def main(args):
    test_results = []

    if not args.no_packetloss_test:
        drop_package_test = rpd.main(args)

        for test in drop_package_test:
            for title in test:
                test_results.append(create_json(title, "packet loss", "%", "Datarate", "Mbit/s", test[title]))

    if not args.no_datarate_test:
        datarate_test = rd.main(args)

        for test in datarate_test:
            for title in test:
                test_results.append(create_json(title, "nodes", "", "Datarate", "Mbit/s", test[title]))

    if not args.no_latency_test:
        latency_test = rlt.main(args)

        for test in latency_test:
            for title in test:
                test_results.append(create_json(title, "nodes", "", "Latency", "ms", test[title]))

    write_json(test_results)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = 'RINA/IP Comparison',
        description = 'Executes different performance test in a RINA/rlite and a TCP/IP network'
    )

    parser.add_argument('-npt', '--no-packetloss-test', action='store_true',
                        default=False,
                        help='Skip the datarate with packetloss test.') 
    parser.add_argument('-ndt', '--no-datarate-test', action='store_true',
                        default=False,
                        help='Skip the datarate test.') 
    parser.add_argument('-nlt', '--no-latency-test', action='store_true',
                        default=False,
                        help='Skip the latency test.')
    parser.add_argument('-s', '--samples', action='store',
                        default=4, type=int,
                        help='Number of samples (repetitions) to take per test.')
    parser.add_argument('-r', '--retries', action='store',
                        default=10, type=int,
                        help='Maximum number of retries for a failed test.')
    parser.add_argument('-n', '--nodes', nargs='+', help='Number of nodes to simulate (list)', required=False, default=[3, 6, 9],
                        type=int)
    parser.add_argument('-ls', '--loss-start', action='store',
                        default=0.05, type=float,
                        help='Start packet loss')
    parser.add_argument('-li', '--loss-increase', action='store',
                        default=0.05, type=float,
                        help='Packet loss increase')
    parser.add_argument('-lm', '--loss-max', action='store',
                        default=0.3, type=float,
                        help='Maximum packet loss')

    args = parser.parse_args()


    main(args)

