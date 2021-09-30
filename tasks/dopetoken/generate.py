#!/usr/bin/env python3

import hmac
import json
import jwt
import os
import sys

PREFIX = "school_nuclear_such_danger_much_destruction_"
SECRET1 = b"hfis08abuarenae0bae8ba0e8bha0e8btah308201314"
SALT1_SIZE = 32
SECRET2 = b"sodifjaosdinbaodunbkdajnbzvwyr024ghewbwebtae"
SALT2_SIZE = 12
SECRET0 = "-----BEGIN PRIVATE KEY-----\nMIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgwVnQsu5s5wge2wG7\nBWEHWg0oNd0jIuQjOxORqsb2s6GhRANCAARFnygpaqyKOeZJmQ+L5qMBo/LBeFTs\ntorSb8I425wIMX6aP9oMJNAzbdVrslFkLrcm84HnlsJS2uPQLGjXq41q\n-----END PRIVATE KEY-----"


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

    payload = {"sub": "XekKekAnon1337", "iat": 1630000199, "nbf": 1630000199, "exp": 1630086599}
    cookie = jwt.encode(payload, SECRET0, algorithm="ES256") # non deterministic

    json.dump({"flags": [flag], "substitutions": {"cookie": cookie},
               "urls": [f"https://dopetoken.school.teamteam.dev/{token}/"]}, sys.stdout)


if __name__ == "__main__":
    generate()
