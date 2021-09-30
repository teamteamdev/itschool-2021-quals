#!/usr/bin/env bash

set -euxo pipefail
shopt -s inherit_errexit
shopt -s nullglob

if="$(route | grep '^default' | grep -o '[^ ]*$')"
localIp="$(ip -o -4 addr list "$if" | awk '{print $4}' | cut -d/ -f1)"
gw="$(getent hosts gateway | cut -f 1 -d ' ')"

tunnelId="$(echo "$localIp" | cut -d. -f4)"
tunnelIp="172.28.2.$tunnelId"

ip link add name gw0 type gretap local "$localIp" remote "$gw"
ip link set gw0 up
ip addr add "$tunnelIp/24" dev gw0
ip route del default
ip route add default via 172.28.2.1 dev gw0

sleep 0.5

(
  for i in $(seq 1 "$INTERNAL_REQUESTS"); do
    sleep "$(bc -l <<< "($RANDOM / 32767) * 3")"
    curl -sk --http1.0 -A "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Ugra/2008070208 Firefox/3.0.1" "https://securesolutions.school.teamteam.dev/$TOKEN/" -u "$INTERNAL_NAME:$INTERNAL_PWD" >/dev/null
  done
) &

(
  for i in $(seq 1 "$EXTERNAL_REQUESTS"); do
    sleep "$(bc -l <<< "($RANDOM / 32767) * 3")"
    curl -sk --http1.0 -A "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Ugra/2008070208 Firefox/3.0.1" "https://funnyvideos.school.teamteam.dev/$TOKEN/" -u "$EXTERNAL_NAME:$EXTERNAL_PWD" >/dev/null
  done
) &

wait
touch "/root/output/$HOSTNAME"
chown "$PARENT_UID:$PARENT_GID" "/root/output/$HOSTNAME"
