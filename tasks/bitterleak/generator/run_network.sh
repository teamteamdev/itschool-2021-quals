#!/usr/bin/env bash

set -euxo pipefail
shopt -s inherit_errexit
shopt -s nullglob

workdir="$1"
shift

outputdir="$TMPDIR/output"
gendir="$(dirname "${BASH_SOURCE[0]}")"

(
  touch /tmp/bitterleak-generator-lock
  exec {lockFd}<>/tmp/bitterleak-generator-lock
  flock "$lockFd"

  cd "$gendir"
  mkdir "$outputdir"
  export OUTPUTDIR="$outputdir"
  export UID
  export GID="$(id -g)"
  docker-compose up --build -d >&2
  docker-compose logs -f >&2 &

  echo "Waiting for finish" >&2
  i=0
  while true; do
    good=1
    for user in $USERS; do
      if [ ! -f "$outputdir/$user" ]; then
        good=""
        break
      fi
    done
    if [ -n "$good" ]; then
      break
    fi

    i=$((i+1))
    if (( i >= 60 )); then
      echo "Timeout" >&2
      exit 1
    fi
    sleep 1
  done
  docker-compose down -t 1 -v --remove-orphans >&2
)

editcap -F libpcap "$outputdir/dump.pcapng" "$outputdir/dump.pcap"
tcprewrite --fixcsum --infile="$outputdir/dump.pcap" --outfile="$workdir/dump.pcap"
cp "$outputdir/sslkeys.txt" "$workdir/sslkeys.txt"
