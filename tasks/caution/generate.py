#!/usr/bin/env python3

import hmac
import json
import os
import sys

PREFIX = "school_sometimes_it_is_enough_to_simply_reach_out_"
SECRET = b"jsajd0a8nw003a[arlhus;reiaslfd;flsi;dfaohdsf"
SALT_SIZE = 12


def get_flag():
    user_id = sys.argv[1]
    return PREFIX + hmac.new(SECRET, str(user_id).encode(), "sha256").hexdigest()[:SALT_SIZE]


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    flag = get_flag()

    json.dump({"flags": [flag], "substitutions": {"flag": flag}, "urls": []}, sys.stdout)


if __name__ == "__main__":
    generate()
