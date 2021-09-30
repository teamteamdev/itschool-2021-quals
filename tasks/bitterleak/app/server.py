#!/usr/bin/env python3

import asyncio
import random
import hashlib
import hmac
import os
import sys
import tempfile
from dataclasses import dataclass

from aiohttp import BasicAuth, hdrs
import aiohttp.web as web
import aiohttp_jinja2 as jinja2

from jinja2 import FileSystemLoader

BASE_DIR = os.path.dirname(__file__)
STATE_DIR = sys.argv[1] if len(sys.argv) >= 2 else BASE_DIR

PREFIX = "school_use_different_passwords_"
SECRET2 = b"aXHn3sY5MYC9T1MR9qPvIYKPxJp9SNKa"
SALT2_SIZE = 12
PASSWORD_SIZE = 8

INTERNAL_USER_AGENT = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.1) Ugra/2008070208 Firefox/3.0.1"


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

    users = [get_user(1, "StrikerXXL", "badpassword4"), get_user(2, "Vadim2004", "King00H"), get_user(3, "XoXoXoX", "vasileva!")]
    return users


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]


def parse_auth_header(request):
    auth_header = request.headers.get(hdrs.AUTHORIZATION)
    if not auth_header:
        return None
    try:
        auth = BasicAuth.decode(auth_header=auth_header)
    except ValueError:
        auth = None
    return auth


def throw_auth(realm):
    raise web.HTTPUnauthorized(
            headers={
                hdrs.WWW_AUTHENTICATE: 'Basic realm="%s"' % realm,
                hdrs.CONTENT_TYPE: 'text/html; charset=utf-8',
                hdrs.CONNECTION: 'keep-alive'
            }
        )


def check_auth(realm, users, request):
    auth = parse_auth_header(request)
    if auth is None:
        throw_auth(realm)
    user = users.get(auth.login)
    if user is None or user[0] != auth.password:
        throw_auth(realm)
    return user[1]


async def main_internal(request):
    token = request.match_info["token"]
    users = {user.internal_name: (user.internal_pwd, user) for user in get_users(token)}
    user = check_auth("securesolutions", users, request)
    return jinja2.render_template("securesolutions.html", request, {"user": user.internal_name})


async def main_external(request):
    token = request.match_info["token"]
    users = {user.external_name: (user.external_pwd, user) for user in get_users(token)}
    user = check_auth("funnyvideos", users, request)
    agent = request.headers.get("User-Agent", "")
    flag = get_flag(token) if user.malicious and agent != INTERNAL_USER_AGENT else None
    return jinja2.render_template("funnyvideos.html", request, {"user": user.external_name, "flag": flag})


def build_app():
    app = web.Application()
    routes = web.RouteTableDef()

   
    @routes.get("/{token}/")
    async def main(request):
        host = request.headers.get("Host", "")
        if host == "securesolutions":
            return await main_internal(request)
        else:
            return await main_external(request)

    app.add_routes(routes)
    jinja2.setup(app, loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")))
    return app


def start():
    app = build_app()
    loop = asyncio.get_event_loop()

    if os.environ.get("DEBUG") == "F":
        web.run_app(app, host="0.0.0.0", port=31337)
    else:
        web.run_app(app, path=os.path.join(tempfile.gettempdir(), "bitterleak.sock"))


if __name__ == "__main__":
    start()
