#!/usr/bin/env python3

import hmac
import json
import os
import sys

PREFIX = "school_now_you_can_learn_about_them_all_"
SECRET1 = b"9eu4ijr2222222222298ew0iphr2222gemhrnvakwere"
SALT1_SIZE = 32
SECRET2 = b"oidsjz0ns9nwnv2u3n0324utr0vau4ntuerngoihdsfo"
SALT2_SIZE = 12


def get_user_tokens():
    user_id = sys.argv[1]

    token = hmac.new(SECRET1, str(user_id).encode(), "sha256").hexdigest()[:SALT1_SIZE]
    flag = PREFIX + hmac.new(SECRET2, token.encode(), "sha256").hexdigest()[:SALT2_SIZE]

    return token, flag


def generate():
    if len(sys.argv) < 3:
        print("Usage: generate.py user_id target_dir", file=sys.stderr)
        sys.exit(1)

    token, flag = get_user_tokens()

    json.dump({"flags": [flag], "substitutions": {}, "urls": [f"https://famous.school.teamteam.dev/{token}/"]}, sys.stdout)


if __name__ == "__main__":
    generate()
