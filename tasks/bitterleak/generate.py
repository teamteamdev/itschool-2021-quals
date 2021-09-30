#!/usr/bin/env python3

import hmac
import random
import subprocess
import json
import os
import sys
from dataclasses import dataclass

PREFIX = "school_use_different_passwords_"
SECRET1 = b"hKSIwAYNpgGBEomO4yM3ZxVLlHFGIopR"
SALT1_SIZE = 32
SECRET2 = b"aXHn3sY5MYC9T1MR9qPvIYKPxJp9SNKa"
SALT2_SIZE = 12
PASSWORD_SIZE = 8


@dataclass
class CorporateSlave:
    malicious: bool
    internal_name: str
    external_name: str
    internal_pwd: str
    external_pwd: str
    internal_requests: int
    external_requests: int


def get_user_password(token, id):
    return hmac.new(SECRET2, f"{token}_user{id}".encode(), "sha256").hexdigest()[:PASSWORD_SIZE]


def get_users(token):
    rand = random.Random(hmac.new(SECRET2, token.encode(), "sha256").hexdigest())
    malicious_user = rand.randint(1, 3)

    def get_user(id, default_name, default_pwd):
        malicious = malicious_user == id
        internal_name = f"user00{id}"
        external_name = default_name if not malicious else internal_name
        internal_pwd = get_user_password(token, id)
        external_pwd = default_pwd if not malicious else internal_pwd
        internal_requests = rand.randint(3, 6)
        external_requests = rand.randint(2, 4) if malicious_user != id else rand.randint(8, 12)
        return CorporateSlave(
            malicious=malicious,
            internal_name=internal_name,
            external_name=external_name,
            internal_pwd=internal_pwd,
            external_pwd=external_pwd,
            internal_requests=internal_requests,
            external_requests=external_requests,
        )

    return [get_user(1, "StrikerXXL", "badpassword4"), get_user(2, "Vadim2004", "King00H"), get_user(3, "XoXoXoX", "vasileva!")]


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
    users = get_users(token)
    gen_env = os.environ.copy()
    gen_env["TOKEN"] = token
    gen_env["USERS"] = " ".join([f"user{i}" for i, user in enumerate(users)])
    for i, user in enumerate(users):
        gen_env[f"USER{i}_INTERNAL_NAME"] = user.internal_name
        gen_env[f"USER{i}_EXTERNAL_NAME"] = user.external_name
        gen_env[f"USER{i}_INTERNAL_PWD"] = user.internal_pwd
        gen_env[f"USER{i}_EXTERNAL_PWD"] = user.external_pwd
        gen_env[f"USER{i}_INTERNAL_REQUESTS"] = str(user.internal_requests)
        gen_env[f"USER{i}_EXTERNAL_REQUESTS"] = str(user.external_requests)
    subprocess.run(["generator/run_network.sh", sys.argv[2]], check=True, env=gen_env)

    json.dump({"flags": [flag]}, sys.stdout)


if __name__ == "__main__":
    generate()
