# -*- coding: utf-8 -*-
#14-6-30
# create by: snower

import logging
import json
import zlib
from tornado.ioloop import IOLoop
from tornado.concurrent import Future
from tornado import gen
from tornado import httputil
from tornado.web import Application as BaseApplication, HTTPError, _RequestDispatcher as _BaseRequestDispatcher
import settings

access_log = logging.getLogger()

class HTTPServerRequest(httputil.HTTPServerRequest):
    def parse_body_arguments(self, content_type, body, headers=None):
        if headers and 'Content-Encoding' in headers:
            if headers["Content-Encoding"] == "gzip":
                body = zlib.decompress(body, zlib.MAX_WBITS|16)
            else:
                httputil.gen_log.warning("Unsupported Content-Encoding: %s",
                                headers['Content-Encoding'])
                return
        if content_type.startswith("application/x-www-form-urlencoded"):
            try:
                uri_arguments = httputil.parse_qs_bytes(httputil.native_str(body), keep_blank_values=True)
            except Exception as e:
                httputil.gen_log.warning('Invalid x-www-form-urlencoded body: %s', e)
                uri_arguments = {}
            for name, values in uri_arguments.items():
                if values:
                    self.body_arguments.setdefault(name, []).extend(values)
        elif content_type.startswith("multipart/form-data"):
            try:
                fields = content_type.split(";")
                for field in fields:
                    k, sep, v = field.strip().partition("=")
                    if k == "boundary" and v:
                        httputil.parse_multipart_form_data(httputil.utf8(v), body, self.body_arguments, self.files)
                        break
                else:
                    raise ValueError("multipart boundary not found")
            except Exception as e:
                httputil.gen_log.warning("Invalid multipart/form-data: %s", e)
        elif content_type.startswith("application/json"):
            if body:
                try:
                    self.body_arguments = json.loads(body)
                except Exception as e:
                    httputil.gen_log.warning("Invalid application/json-data: %s", e)

    def _parse_body(self):
        self.parse_body_arguments(
            self.headers.get("Content-Type", ""), self.body,
            self.headers)

        if isinstance(self.body_arguments, dict):
            for k, v in self.body_arguments.items():
                if isinstance(v, (tuple, list)):
                    self.arguments.setdefault(k, []).extend(v)
                else:
                    self.arguments.setdefault(k, []).append(v)


class _RequestDispatcher(_BaseRequestDispatcher):
    def execute(self):
        self.handler = self.handler_class(self.application, self.request,
                                          **self.handler_kwargs)
        transforms = [t(self.request) for t in self.application.transforms]

        if self.stream_request_body:
            self.handler._prepared_future = Future()
        f = self.handler._execute(transforms, *self.path_args, **self.path_kwargs)
        f.add_done_callback(lambda f: f.exception())
        return self.handler._prepared_future

    def headers_received(self, start_line, headers):
        self.set_request(HTTPServerRequest(
            connection=self.connection, start_line=start_line,
            headers=headers))
        if self.stream_request_body:
            self.request.body = Future()
            return self.execute()

class Application(BaseApplication):
    def __init__(self, *args,**kwargs):
        super(Application,self).__init__(*args, **kwargs)

        self.formater = None
        self.serialize = None
