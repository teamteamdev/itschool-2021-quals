#!/usr/bin/env nix-shell
#!nix-shell -i sh -p python3 -p utillinux -p docker-compose -p wireshark-cli -p tcpreplay

exec ./generate.py "$@"
