#!/bin/bash

echo "=== Network Debugging ==="

echo -e "\n--- Hostname Information ---"
hostname
hostname -f
hostname -A

echo -e "\n--- IP Addresses ---"
ip addr show

echo -e "\n--- Listening Ports ---"
netstat -tuln

echo -e "\n--- Network Interfaces ---"
ifconfig -a

echo -e "\n--- DNS Configuration ---"
cat /etc/resolv.conf

echo -e "\n--- Routing Table ---"
route -n

echo -e "\n--- Firewall Rules ---"
sudo iptables -L

