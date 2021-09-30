#!/usr/bin/env python3

import hmac
import json
import os
import sys

PREFIX = "school_can_you_feel_it_of_course_not_"
SECRET1 = b"jiufdhbfdgubhsdafkbvjsiukfnbdmkshugkbnkjsfaj"
SALT1_SIZE = 32
SECRET2 = b"jfzd09b8s7truwnpg5iyrsnfa9843uuuuu9ircf2201e"
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

    json.dump({"flags": [flag], "substitutions": {}, "urls": [f"https://electrotech.school.teamteam.dev/{token}/"]}, sys.stdout)


if __name__ == "__main__":
    generate()
