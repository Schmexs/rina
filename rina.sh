#! /bin/bash

# User Input how many Network Namespaces you want to create and which topology you want to use
echo "Which topology do you want to use? (1)Line (2)Fully meshed (3)Redundant paths"
read -p "Enter a number: " topology


echo "How many Network Namespaces do you want to create?"
read -p "Enter a number: " number


# Create the Network Namespaces
for ((i=1; i<=$number; i++))
do
    echo "Creating namespace $i"
    ip netns add node$i
done

# Create the veth pairs for line topology
if [[ $topology == "1" ]]; then
for ((i=1; i<=$number-1; i++)); 
do
    next=$((i+1))
    ip link add veth$i"-"$next type veth peer name veth$next"-"$i
    ip link set veth$i"-"$next netns node$i
    ip link set veth$next"-"$i netns node$next
    ip netns exec node$i ip addr add 10.0.$i.1/24 dev veth$i"-"$next
    ip netns exec node$next ip addr add 10.0.$i.2/24 dev veth$next"-"$i
    ip netns exec node$i ip link set veth$i"-"$next up
    ip netns exec node$next ip link set veth$next"-"$i up
    ip netns exec node$i ip link set lo up
    ip netns exec node$next ip link set lo up
done

# Create the veth pairs for fully meshed topology
elif [[ $topology == "2" ]]; then
for ((i=1; i<=$number; i++));
do
  for ((j=1; j<=$number; j++)); then
    if [[ $i != $j ]]; then
        ip link add veth$i-$j type veth peer name veth$j-$i
        ip link set veth$i-$j netns node$i
        ip link set veth$j-$i netns node$j
        ip addr add 10.0.$i.$j/24 dev veth$i-$j
    fi
  do
done
fi

# Create routing tables for each namespace
for ((i=1; i<=$number; i++))
do
    ip netns exec node$i ip route add default via 10.0.$i.1
done



