#!/usr/bin/env python3

import aiohttp.web as web
import aiohttp_jinja2 as jinja2
import asyncio
import tempfile
import hmac
import jwt
import os
import sys
import time
from jinja2 import FileSystemLoader

BASE_DIR = os.path.dirname(__file__)
STATE_DIR = sys.argv[1] if len(sys.argv) >= 2 else BASE_DIR

PREFIX = "school_nuclear_such_danger_much_destruction_"
SECRET2 = b"sodifjaosdinbaodunbkdajnbzvwyr024ghewbwebtae"
SALT2_SIZE = 12

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAERZ8oKWqsijnmSZkPi+ajAaPywXhU
7LaK0m/CONucCDF+mj/aDCTQM23Va7JRZC63JvOB55bCUtrj0Cxo16uNag==
-----END PUBLIC KEY-----"""


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]


def process_cookie(cookie):
    if not cookie:
        return "no-cookie"

    # here we emulate bug presented in popular jwt libraries,
    # because pyjwt has good patches for it

    try:
        header = jwt.get_unverified_header(cookie)

        if header["alg"] == "none":
            if not cookie.endswith(".") or cookie.count(".") > 2:
                raise jwt.exceptions.DecodeError()
            data = jwt.decode(
                cookie,
                algorithms=["none"],
                options={
                    "verify_signature": False,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "require": ["iat", "sub", "exp", "nbf"]
                }
            )
        else:
            data = jwt.decode(
                cookie,
                PUBLIC_KEY,
                algorithms=["ES256"],
                options={
                    "require": ["iat", "sub", "exp", "nbf"]
                }
            )
    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.InvalidAlgorithmError):
        return "invalid-signature"
    except jwt.exceptions.DecodeError:
        return "non-jwt-cookie"
    except (jwt.exceptions.InvalidIssuedAtError, jwt.exceptions.ImmatureSignatureError):
        return "time-broken"
    except jwt.exceptions.ExpiredSignatureError:
        return "expired"
    except jwt.exceptions.MissingRequiredClaimError:
        return "missing-fields"
    except Exception:
        return "jwt-error"

    if data["exp"] - data["iat"] > 86400:
        return "weak"
    if data["iat"] != data["nbf"]:
        return "time-broken"
    if data["sub"] != "XekKekAnon1337":
        return "unknown-user"

    return None  # OK


def build_app():
    app = web.Application()
    routes = web.RouteTableDef()
    
    @routes.get("/{token}/")
    async def main(request):
        token = request.match_info["token"]

        cookie = request.cookies.get("session")
        cookie_error = process_cookie(cookie)

        if not cookie_error:
            return jinja2.render_template("conversation.html", request, {"token": token, "flag": get_flag(token)})
        else:
            return jinja2.render_template("form.html", request, {"error": cookie_error})
        

    @routes.post("/{token}/")
    async def post(request):
        return jinja2.render_template("form.html", request, {"error": "wrong-password"})


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
        web.run_app(app, path=os.path.join(tempfile.gettempdir(), "dopetoken.sock"))


if __name__ == "__main__":
    start()
