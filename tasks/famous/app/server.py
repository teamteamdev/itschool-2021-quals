#!/usr/bin/env python3

import aiohttp.web as web
import aiohttp_jinja2 as jinja2
import asyncio
import tempfile
import hashlib
import hmac
import json
import os
import sys
from jinja2 import FileSystemLoader

BASE_DIR = os.path.dirname(__file__)
STATE_DIR = sys.argv[1] if len(sys.argv) >= 2 else BASE_DIR

PREFIX = "school_now_you_can_learn_about_them_all_"
SECRET2 = b"oidsjz0ns9nwnv2u3n0324utr0vau4ntuerngoihdsfo"
SALT2_SIZE = 12

REFERENCE = json.load(open(os.path.join(BASE_DIR, "reference", "result.json")))


def person_hash(person):
    representation = json.dumps([person["name"], person["born"], person["died"],
                                 person["pic"].replace("_", " ") if person["pic"] else None])
    return hashlib.sha1(representation.encode()).hexdigest()


def get_flag(token):
    return PREFIX + hmac.new(SECRET2, token.encode(), 'sha256').hexdigest()[:SALT2_SIZE]


def build_app():
    app = web.Application()
    routes = web.RouteTableDef()
    
    @routes.get("/{token}/")
    async def main(request):
        return jinja2.render_template("base.html", request, {})
    

    @routes.post("/{token}/")
    async def main(request):
        token = request.match_info["token"]
        flag = get_flag(token)

        data_text = (await request.post())["data"]

        try:
            data = list(json.loads(data_text))
        except KeyError:
            return jinja2.render_template("base.html", request, {"data": data_text, "error": "Поле не заполнено"})
        except json.decoder.JSONDecodeError as e:
            return jinja2.render_template("base.html", request, {"data": data_text, "error": str(e)})

        try:
            data_hashes = {person_hash(p) for p in data}
            ref_hashes = {person_hash(p) for p in REFERENCE}

            try:
                rate1 = len(data_hashes & ref_hashes) / len(ref_hashes)
                rate2 = len(data_hashes | ref_hashes) / len(data_hashes)
                rate = min(rate1, 1 / rate2)
            except ZeroDivisionError:
                rate = 0
        except TypeError:
            return jinja2.render_template("base.html", request, {"data": data_text, "error": "Неверный тип данных"})
        except KeyError:
            return jinja2.render_template("base.html", request, {"data": data_text, "error": "Отсутствует поле " + str(e)})

        return jinja2.render_template("base.html", request, {"data": data_text, "rate": rate, "flag": flag if rate >= 0.75 else None})


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
        web.run_app(app, path=os.path.join(tempfile.gettempdir(), "famous.sock"))


if __name__ == "__main__":
    start()
