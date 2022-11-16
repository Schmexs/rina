#! /bin/bash

ip -all netns delete    

ip netns add nodeA
ip netns add nodeB
ip netns add nodeC
ip netns add nodeD

ip link add veth0 type veth peer name veth1
ip link add veth2 type veth peer name veth3
ip link add veth4 type veth peer name veth5

ip netns exec nodeD ip link set dev lo up
ip link set veth5 netns nodeD
ip netns exec nodeD ip addr add 10.10.1.6/24 dev veth5
ip netns exec nodeD ip link set dev veth5 up


ip netns exec nodeC ip link set dev lo up
ip link set veth3 netns nodeC
ip netns exec nodeC ip addr add 10.10.1.4/24 dev veth3
ip netns exec nodeC ip link set dev veth3 up
ip link set veth4 netns nodeC
ip netns exec nodeC ip addr add 10.10.1.5/24 dev veth4
ip netns exec nodeC ip link set dev veth4 up

ip netns exec nodeB ip link set dev lo up
ip link set veth1 netns nodeB
ip netns exec nodeB ip addr add 10.10.1.2/24 dev veth1
ip netns exec nodeB ip link set dev veth1 up
ip link set veth2 netns nodeB
ip netns exec nodeB ip addr add 10.10.1.3/24 dev veth2
ip netns exec nodeB ip link set dev veth2 up

ip netns exec nodeA ip link set dev lo up
ip link set veth0 netns nodeA
ip netns exec nodeA ip addr add 10.10.1.1/24 dev veth0
ip netns exec nodeA ip link set dev veth0 up

sudo modprobe rlite
sudo modprobe rlite-normal
sudo modprobe rlite-shim-eth

ip netns exec nodeA sudo rlite-uipcps &

ip netns exec nodeA sudo ip link set veth0 up
ip netns exec nodeA sudo rlite-ctl ipcp-create ethAB.IPCP shim-eth ethAB.DIF
ip netns exec nodeA sudo rlite-ctl ipcp-config ethAB.IPCP netdev veth0
ip netns exec nodeA sudo rlite-ctl ipcp-create a.IPCP normal n.DIF
ip netns exec nodeA sudo rlite-ctl ipcp-register a.IPCP ethAB.DIF

ip netns exec nodeB sudo rlite-uipcps &

ip netns exec nodeB sudo ip link set veth1 up
ip netns exec nodeB sudo rlite-ctl ipcp-create ethAB.IPCP shim-eth ethAB.DIF
ip netns exec nodeB sudo rlite-ctl ipcp-config ethAB.IPCP netdev veth1
ip netns exec nodeB sudo rlite-ctl ipcp-create b.IPCP normal n.DIF
ip netns exec nodeB sudo rlite-ctl ipcp-register b.IPCP ethAB.DIF
ip netns exec nodeB sudo ip link set veth2 up
ip netns exec nodeB sudo rlite-ctl ipcp-create ethBC.IPCP shim-eth ethBC.DIF
ip netns exec nodeB sudo rlite-ctl ipcp-config ethBC.IPCP netdev veth2
ip netns exec nodeB sudo rlite-ctl ipcp-register b.IPCP ethBC.DIF

ip netns exec nodeC sudo rlite-uipcps &

ip netns exec nodeC sudo ip link set veth3 up
ip netns exec nodeC sudo rlite-ctl ipcp-create ethBC.IPCP shim-eth ethBC.DIF
ip netns exec nodeC rlite-ctl ipcp-config ethBC.IPCP netdev veth3
ip netns exec nodeC rlite-ctl ipcp-create c.IPCP normal n.DIF
ip netns exec nodeC rlite-ctl ipcp-register c.IPCP ethBC.DIF
ip netns exec nodeC sudo ip link set veth4 up
ip netns exec nodeC sudo rlite-ctl ipcp-create ethCD.IPCP shim-eth ethCD.DIF
ip netns exec nodeC sudo rlite-ctl ipcp-config ethCD.IPCP netdev veth4
ip netns exec nodeC sudo rlite-ctl ipcp-register c.IPCP ethCD.DIF


ip netns exec nodeD sudo rlite-uipcps &

ip netns exec nodeD sudo ip link set veth5 up
ip netns exec nodeD sudo rlite-ctl ipcp-create ethCD.IPCP shim-eth ethCD.DIF
ip netns exec nodeD rlite-ctl ipcp-config ethCD.IPCP netdev veth5
ip netns exec nodeD rlite-ctl ipcp-create d.IPCP normal n.DIF
ip netns exec nodeD rlite-ctl ipcp-register d.IPCP ethCD.DIF




ip netns exec nodeB sudo rlite-ctl ipcp-enroller-enable b.IPCP   
ip netns exec nodeC sudo rlite-ctl ipcp-enroller-enable c.IPCP
ip netns exec nodeA sudo rlite-ctl ipcp-enroll a.IPCP n.DIF ethAB.DIF b.IPCP  
ip netns exec nodeC sudo rlite-ctl ipcp-enroll c.IPCP n.DIF ethBC.DIF b.IPCP 
ip netns exec nodeD sudo rlite-ctl ipcp-enroll d.IPCP n.DIF ethCD.DIF c.IPCP 