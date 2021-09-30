#!/usr/bin/env bash

set -euxo pipefail
shopt -s inherit_errexit
shopt -s nullglob

internalIf="$(ip -br -4 addr | grep 172.28.0. | grep -o '^[^@ ]*')"
localIp="$(ip -o -4 addr list "$internalIf" | awk '{print $4}' | cut -d/ -f1)"
externalIf="$(route | grep '^default' | grep -o '[^ ]*$')"

iptables -t nat -A POSTROUTING -o "$externalIf" -j MASQUERADE
brctl addbr br0
iptables -t nat -A PREROUTING -i br0 -p tcp --dport 80 -j REDIRECT --to-port 8080
iptables -t nat -A PREROUTING -i br0 -p tcp --dport 443 -j REDIRECT --to-port 8080
ip addr add 172.28.2.1/24 dev br0

ifaces=""
add_tunnel() {
  local tunnelIf="$1"
  local remoteUser="$2"
  local remoteIp="$(getent hosts "$remoteUser" | cut -f 1 -d ' ')"
  local tunnelId="$(echo "$remoteIp" | cut -d. -f4)"
  local remoteTunnelIp="172.28.2.$tunnelId"

  ip link add name "$tunnelIf" type gretap local "$localIp" remote "$remoteIp"
  ip link set "$tunnelIf" up
  brctl addif br0 "$tunnelIf"
  ifaces="$ifaces -i $tunnelIf"
}

tun_id=0
for user in $USERS; do
  add_tunnel "user$tun_id" "$user"
  tun_id=$((tun_id+1))
done

ip link set br0 up

touch /root/output/{dump.pcapng,sslkeys.txt}
chown "$PARENT_UID:$PARENT_GID" /root/output/{dump.pcapng,sslkeys.txt}
chmod 666 /root/output/{dump.pcapng,sslkeys.txt}

export SSLKEYLOGFILE="/root/output/sslkeys.txt"
tshark $ifaces -w /root/output/dump.pcapng &
mitmdump --mode transparent &
wait
