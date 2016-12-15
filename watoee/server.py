# -*- coding: utf-8 -*-
#14-6-28
# create by: snower

import time
import logging
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from application import Application
from urls import urls
import settings

application = None
server = None
ioloop = None

def start():
    global application, server, ioloop
    application = Application(urls, debug=settings.DEBUG, autoreload=False)
    server = HTTPServer(application, xheaders=True)
    server.bind(4700)
    server.start(2)
    ioloop = IOLoop.instance()
    ioloop.add_callback(application.start)
    ioloop.start()

def stop():
    global application, server, ioloop
    ioloop = IOLoop.current()
    def _():
        application.stop()
        server.stop()
        start_time = time.time()
        def stop_loop():
            now = time.time()
            if ioloop._callbacks or ioloop._timeouts:
                if start_time + 1.5 < now:
                    logging.info("stop error: %s %s", ioloop._callbacks, ioloop._timeouts)
                    ioloop.stop()
                else:
                    ioloop.add_timeout(now + 0.5, stop_loop)
            else:
                ioloop.stop()
        stop_loop()
    ioloop.add_callback_from_signal(_)