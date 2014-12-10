#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import json
import random

import requests
import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.options import define, options, parse_command_line

define("port", default=3100, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")
define("xheaders", default=True, help="use X-headers")
define("cookie_secret", default="secret key", help="secure key")

d = os.path.dirname
fn = os.path.join(d(os.path.abspath(__file__)), "static", "facts.json")
with open(fn, "r") as f:
    facts = json.load(f)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/fact", FactHandler),
            (r"/fact.txt", FactTxtHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            xheaders=options.xheaders,
            cookie_secret=options.cookie_secret,
            debug=options.debug,
        )
        super(Application, self).__init__(handlers, **settings)


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        username = self.get_argument("username", None)
        if username is not None:
            params = dict(
                username=username,
                api_token=os.environ.get("YO_API_KEY", None),
                link="http://yo.dfm.io/fact",
            )
            requests.post("https://api.justyo.co/yo/", data=params)
        self.render("fact.html", fact="\"YO AT ME\" — YOBOT3K")


class FactHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("fact.html", fact=facts[random.randint(0, len(facts))])


class FactTxtHandler(tornado.web.RequestHandler):

    def get(self):
        self.set_header("Content-Type", "text/plain")
        self.write(facts[random.randint(0, len(facts))])


def main():
    parse_command_line()

    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port, address="127.0.0.1")
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
