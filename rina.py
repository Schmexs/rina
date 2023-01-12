import subprocess
import logging
import typing

logger = logging.getLogger("rina-eval")
logger.setLevel(logging.DEBUG)


def flatten(args):
    for item in args:
        if isinstance(item, str):
            yield item
        elif isinstance(item, typing.Sequence):
            yield from item
        else:
            yield str(item)


def run(*args, check=True, text=True, netns=None, **kwargs):
    command_list = list(flatten(args))

    if netns is not None:
        command_list = ['ip', 'netns', 'exec', netns] + command_list

    logger.debug('> ' + ' '.join(command_list))

    process = subprocess.run(command_list, text=text, **kwargs)
    if check and process.returncode != 0:
        error = process.stderr.strip() if process.stderr else f'exit code {process.returncode}'
        error_msg = f'subprocess failed: {" ".join(command_list)}: {error}'
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    return process.stdout


def cleanup():
    run('ip', '-all', 'netns', 'delete')
    try:
        run('killall', 'bird')
        run('killall', 'rlite-uipcp')
    except RuntimeError:
        pass


def create_networknamespaces(number):
    for i in range(number):
        run('ip', 'netns', 'add', f'node{i}')


def load_rlite():
    run('modprobe', 'rlite')
    run('modprobe', 'rlite-normal')
    run('modprobe', 'rlite-shim-eth')
    set_sysctl()


def set_sysctl():
    run('sysctl', '-w', 'net.ipv4.ip_forward=1')
    run('sysctl', '-w', 'net.ipv4.conf.all.rp_filter=0')


def start_bird(netns_name):
    run('bird', '-c', 'bird.conf', '-P', f'/var/run/bird-{netns_name}.pid', '-s', f'/var/run/bird-{netns_name}.ctl',
        netns=netns_name)


def create_line_topology(number):
    for i in range(number):
        logger.warning(f"Setup node {i}")

        last = number - 1 == i
        next = i + 1

        netns_name = f'node{i}'
        netns_name_next = f'node{i + 1}'
        link_to = f'veth{i}-{next}'
        link_from = f'veth{next}-{i}'

        if last:
            start_bird(netns_name)
            continue

        run('ip', 'link', 'add', link_to, 'type', 'veth', 'peer', 'name', link_from, netns=netns_name)
        run('ip', 'link', 'set', link_from, 'netns', netns_name_next, netns=netns_name)
        run('ip', 'addr', 'add', f'10.0.{i}.1/24', 'dev', link_to, netns=netns_name)
        run('ip', 'addr', 'add', f'10.0.{i}.2/24', 'dev', link_from, netns=netns_name_next)
        run('ip', 'link', 'set', link_to, 'up', netns=netns_name)
        run('ip', 'link', 'set', link_from, 'up', netns=netns_name_next)
        run('ip', 'link', 'set', 'lo', 'up', netns=netns_name)
        run('ip', 'link', 'set', 'lo', 'up', netns=netns_name_next)

        start_bird(netns_name)

        # RINA
        logger.warning(f"Setup RINA base node {i}")

        if i == 0:
            run('bash', '-c', 'rlite-uipcps &', netns=netns_name)
            run('rlite-ctl', 'ipcp-create', f'{netns_name}.IPCP', 'normal', 'n.DIF', netns=netns_name)
            run('rlite-ctl', 'ipcp-enroller-enable', f'{netns_name}.IPCP', netns=netns_name)

        if not last:
            run('bash', '-c', 'rlite-uipcps &', netns=netns_name_next)
            run('rlite-ctl', 'ipcp-create', f'{netns_name_next}.IPCP', 'normal', 'n.DIF', netns=netns_name_next)

        logger.warning(f"Setup RINA node {i}")

        # RINA next
        run('rlite-ctl', 'ipcp-create', f'{link_from}.IPCP', 'shim-eth', f'{link_from}.DIF', netns=netns_name_next)
        run('rlite-ctl', 'ipcp-config', f'{link_from}.IPCP', 'netdev', link_from, netns=netns_name_next)
        run('rlite-ctl', 'ipcp-register', f'{netns_name_next}.IPCP', f'{link_from}.DIF', netns=netns_name_next)

        # RINA current
        run('rlite-ctl', 'ipcp-create', f'{link_to}.IPCP', 'shim-eth', f'{link_to}.DIF', netns=netns_name)
        run('rlite-ctl', 'ipcp-config', f'{link_to}.IPCP', 'netdev', link_to, netns=netns_name)
        run('rlite-ctl', 'ipcp-register', f'{netns_name}.IPCP', f'{link_to}.DIF', netns=netns_name)

        run('rlite-ctl', 'ipcp-enroll', f'{netns_name_next}.IPCP', 'n.DIF', f'{link_from}.DIF', f'{netns_name}.IPCP',
            netns=netns_name_next)

    # perform_test_rina(number)


def create_fully_meshed_topology(number, rina=True):
    created_pairs = set()

    for i in range(number):
        netns_name = f'node{i}'
        run('ip', 'link', 'set', 'lo', 'up', netns=f'node{i}')
        run('bash', '-c', 'rlite-uipcps &', netns=netns_name)
        run('rlite-ctl', 'ipcp-create', f'{netns_name}.IPCP', 'normal', 'n.DIF', netns=netns_name)

    for i in range(number):
        netns_name = f'node{i}'

        if i == 0:
            run('rlite-ctl', 'ipcp-enroller-enable', f'{netns_name}.IPCP', netns=netns_name)

        for j in range(number):
            if i != j and f"{i}-{j}" not in created_pairs and f"{j}-{i}" not in created_pairs:

                if j == 0:
                    continue

                netns_name_other = f'node{j}'
                link_to = f'veth{i}-{j}'
                link_from = f'veth{j}-{i}'

                run('ip', 'link', 'add', link_to, 'type', 'veth', 'peer', 'name', link_from, netns=netns_name)
                run('ip', 'link', 'set', link_from, 'netns', netns_name_other, netns=netns_name)
                run('ip', 'addr', 'add', f'10.{i}.{j}.1/24', 'dev', link_to, netns=netns_name)
                run('ip', 'addr', 'add', f'10.{i}.{j}.2/24', 'dev', link_from, netns=netns_name_other)
                run('ip', 'link', 'set', link_to, 'up', netns=netns_name)
                run('ip', 'link', 'set', link_from, 'up', netns=netns_name_other)

                # RINA
                run('rlite-ctl', 'ipcp-create', f'{link_to}.IPCP', 'shim-eth', f'{link_to}.DIF', netns=netns_name)
                run('rlite-ctl', 'ipcp-config', f'{link_to}.IPCP', 'netdev', link_to, netns=netns_name)
                run('rlite-ctl', 'ipcp-register', f'{netns_name}.IPCP', f'{link_to}.DIF', netns=netns_name)

                # RINA Other
                run('rlite-ctl', 'ipcp-create', f'{link_from}.IPCP', 'shim-eth', f'{link_from}.DIF',
                    netns=netns_name_other)
                run('rlite-ctl', 'ipcp-config', f'{link_from}.IPCP', 'netdev', link_from, netns=netns_name_other)
                run('rlite-ctl', 'ipcp-register', f'{netns_name_other}.IPCP', f'{link_from}.DIF',
                    netns=netns_name_other)

                # RINA Enroll
                run('rlite-ctl', 'ipcp-enroll', f'{netns_name_other}.IPCP', 'n.DIF', f'{link_from}.DIF',
                    f'{netns_name}.IPCP', netns=netns_name_other)

                created_pairs.add(f"{i}-{j}")

        start_bird(netns_name)


def create_redundant_paths_topology(number):
    layer_dict = {}

    for i in range(number):
        netns_name = f'node{i}'
        run('ip', 'link', 'set', 'lo', 'up', netns=f'node{i}')
        run('bash', '-c', 'rlite-uipcps &', netns=netns_name)
        run('rlite-ctl', 'ipcp-create', f'{netns_name}.IPCP', 'normal', 'n.DIF', netns=netns_name)

        actual_layer = int(i / 3) + 1
        if actual_layer in layer_dict:
            layer_dict[int(i / 3) + 1].append(i)
        else:
            layer_dict[int(i / 3) + 1] = [i]

    for layer in layer_dict:
        for i in layer_dict[layer]:
            # Connect Nodes in the same layer
            next = None
            netns_name = None
            next_netns_name = None
            if len(layer_dict[layer]) == 3:
                next = layer_dict[layer][(i + 1) % 3]
                netns_name = f'node{i}'
                next_netns_name = f'node{next}'
            elif len(layer_dict[layer]) == 2 and i+1 in layer_dict[layer]:
                next = i + 1
                netns_name = f'node{i}'
                next_netns_name = f'node{next}'
            else:
                break


            if i == 0:
                run('rlite-ctl', 'ipcp-enroller-enable', f'{netns_name}.IPCP', netns=netns_name)

            link_to = f'veth{i}-{next}'
            link_from = f'veth{next}-{i}'

            run('ip', 'link', 'add', link_to, 'type', 'veth', 'peer', 'name', link_from, netns=netns_name)
            run('ip', 'link', 'set', link_from, 'netns', next_netns_name, netns=netns_name)
            run('ip', 'addr', 'add', f'10.0.{i}.1/24', 'dev', link_to, netns=netns_name)
            run('ip', 'addr', 'add', f'10.0.{i}.2/24', 'dev', link_from, netns=next_netns_name)
            run('ip', 'link', 'set', link_to, 'up', netns=netns_name)
            run('ip', 'link', 'set', link_from, 'up', netns=next_netns_name)

            # RINA
            run('rlite-ctl', 'ipcp-create', f'{link_to}.IPCP', 'shim-eth', f'{link_to}.DIF', netns=netns_name)
            run('rlite-ctl', 'ipcp-config', f'{link_to}.IPCP', 'netdev', link_to, netns=netns_name)
            run('rlite-ctl', 'ipcp-register', f'{netns_name}.IPCP', f'{link_to}.DIF', netns=netns_name)

            # RINA Other
            run('rlite-ctl', 'ipcp-create', f'{link_from}.IPCP', 'shim-eth', f'{link_from}.DIF',
                netns=next_netns_name)
            run('rlite-ctl', 'ipcp-config', f'{link_from}.IPCP', 'netdev', link_from, netns=next_netns_name)
            run('rlite-ctl', 'ipcp-register', f'{next_netns_name}.IPCP', f'{link_from}.DIF',
                netns=next_netns_name)

            # RINA Enroll
            run('rlite-ctl', 'ipcp-enroll', f'{next_netns_name}.IPCP', 'n.DIF', f'{link_from}.DIF',
                f'{netns_name}.IPCP', netns=next_netns_name)

            # Connect Layers
            if layer + 1 in layer_dict:
                next = i + 3
                if next in layer_dict[layer + 1]:
                    netns_name = f'node{i}'
                    next_netns_name = f'node{next}'

                    link_to = f'veth{i}-{next}'
                    link_from = f'veth{next}-{i}'

                    run('ip', 'link', 'add', link_to, 'type', 'veth', 'peer', 'name', link_from, netns=netns_name)
                    run('ip', 'link', 'set', link_from, 'netns', next_netns_name, netns=netns_name)
                    run('ip', 'addr', 'add', f'10.{layer}.{i}.1/24', 'dev', link_to, netns=netns_name)
                    run('ip', 'addr', 'add', f'10.{layer}.{i}.2/24', 'dev', link_from, netns=next_netns_name)
                    run('ip', 'link', 'set', link_to, 'up', netns=netns_name)
                    run('ip', 'link', 'set', link_from, 'up', netns=next_netns_name)

                    # RINA
                    run('rlite-ctl', 'ipcp-create', f'{link_to}.IPCP', 'shim-eth', f'{link_to}.DIF', netns=netns_name)
                    run('rlite-ctl', 'ipcp-config', f'{link_to}.IPCP', 'netdev', link_to, netns=netns_name)
                    run('rlite-ctl', 'ipcp-register', f'{netns_name}.IPCP', f'{link_to}.DIF', netns=netns_name)

                    # RINA Other
                    run('rlite-ctl', 'ipcp-create', f'{link_from}.IPCP', 'shim-eth', f'{link_from}.DIF',
                        netns=next_netns_name)
                    run('rlite-ctl', 'ipcp-config', f'{link_from}.IPCP', 'netdev', link_from, netns=next_netns_name)
                    run('rlite-ctl', 'ipcp-register', f'{next_netns_name}.IPCP', f'{link_from}.DIF',
                        netns=next_netns_name)

                    # RINA Enroll
                    run('rlite-ctl', 'ipcp-enroll', f'{next_netns_name}.IPCP', 'n.DIF', f'{link_from}.DIF',
                        f'{netns_name}.IPCP', netns=next_netns_name)

    # OSPF
    for i in range(number):
        netns_name = f'node{i}'
        start_bird(netns_name)


def perform_test_rina(number):
    run('bash', '-c', 'rinaperf -l -d n.DIF &', netns='node0')
    run('rinaperf', '-d', 'n.DIF', '-t', 'perf', '-s', '1400', '-c', '100000', netns=f'node{number - 1}')


def main():
    cleanup()

    topology = input("Which topology do you want to use? (1)Line (2)Fully meshed (3)Redundant paths: ")
    number = int(input("How many Network Namespaces do you want to create?: "))

    create_networknamespaces(number)
    load_rlite()

    match topology:
        case "1":
            create_line_topology(number)
        case "2":
            create_fully_meshed_topology(number)
        case "3":
            create_redundant_paths_topology(number)
        case _:
            print("Invalid topology")


if __name__ == '__main__':
    main()
