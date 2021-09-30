#!/usr/bin/env python3

import asyncio
import hashlib
import hmac
import os
import sys
import tempfile
import time

import aiohttp.web as web
import aiohttp_jinja2 as jinja2

from jinja2 import FileSystemLoader

BASE_DIR = os.path.dirname(__file__)
STATE_DIR = sys.argv[1] if len(sys.argv) >= 2 else BASE_DIR

PREFIX = "school_can_you_feel_it_of_course_not_"
SECRET2 = b"jfzd09b8s7truwnpg5iyrsnfa9843uuuuu9ircf2201e"
SALT2_SIZE = 12

SECRET0 = b"jakfdsjfdsioan19275oafnvanoirvwoirokjfdvshew"


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]


def build_app():
    app = web.Application()
    routes = web.RouteTableDef()
    
    @routes.get("/{token}/")
    async def main(request):
        token = request.match_info["token"]
        flag = get_flag(token)

        header_hash = lambda t: hashlib.sha1(repr((int(t), token, request.headers.get("user-agent"))).encode() + SECRET0).hexdigest()

        header = request.headers.get("X-I-Am-Robot", "")
        allowed_headers = [header_hash(i) for i in range(int(time.time() - 2), int(time.time() + 1))]

        if header in allowed_headers:
            return jinja2.render_template("base.html", request, {"flag": flag})
        elif header:
            return jinja2.render_template("base.html", request, {"error": True, "header": header_hash(time.time())})
        else:
            return jinja2.render_template("base.html", request, {"header": header_hash(time.time())})


    routes.static("/static", os.path.join(BASE_DIR, "static"))

    app.add_routes(routes)
    jinja2.setup(app, loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")))
    return app


def start():
    app = build_app()
    loop = asyncio.get_event_loop()

    if os.environ.get("DEBUG") == "F":
        web.run_app(app, host="0.0.0.0", port=31337)
    else:
        web.run_app(app, path=os.path.join(tempfile.gettempdir(), "electrotech.sock"))


if __name__ == "__main__":
    start()
