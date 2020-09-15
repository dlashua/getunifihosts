#!/bin/sh
hosts_dir=/etc/dnsmasq.hosts
unifi_hosts=${OUT_FILE:-/tmp/unifi.out}

while true; do
    ./unifi.py > /tmp/current_unifi.hosts
    if [ $? = 0 ] && ! diff -N $unifi_hosts /tmp/current_unifi.hosts; then
        cat /tmp/current_unifi.hosts > $unifi_hosts
    fi
    sleep ${UNIFI_POLL_INTERVAL:-60}
done