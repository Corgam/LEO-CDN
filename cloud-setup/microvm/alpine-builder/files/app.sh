#!/bin/sh

# this optionally sets the gateway as your nameserver to be able to resolve internal
# .celestial IP addresses
IP=$(/sbin/ip route | awk '/default/ { print $3 }')
echo nameserver $IP > /etc/resolv.conf

rc-service dropbear start

read
