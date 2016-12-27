# -*- coding: utf-8 -*-
#14-6-30
# create by: snower

import sys
import functools
import json
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.concurrent import Future
from tornado.web import RequestHandler as BaseRequestHandler, HTTPError
from ..exceptions import ApiHTTPError, ServerError
from ..auth import Config
from .cursor import Cursor


class RequestHandler(BaseRequestHandler):
    def __init__(self, *args, **kwargs):
        self._current_cursor = None
        self._auth_config = Config(self)

        super(RequestHandler, self).__init__(*args, **kwargs)

    @gen.coroutine
    def prepare(self):
        yield self._auth_config.load()

    def finish(self, chunk=None):
        super(RequestHandler, self).finish(chunk)

    def _execute(self, transforms, *args, **kwargs):
        """Executes this request with the given output transforms."""
        self._transforms = transforms
        try:
            if self.request.method not in self.SUPPORTED_METHODS:
                raise HTTPError(405)
            self.path_args = [self.decode_argument(arg) for arg in args]
            self.path_kwargs = dict((k, self.decode_argument(v, name=k))
                                    for (k, v) in kwargs.items())
            self._when_complete(self.prepare(), self._execute_method)
        except Exception as e:
            self._handle_request_exception(e)
        return Future()

    def _when_complete(self, result, callback):
        try:
            if result is None:
                callback()
            elif isinstance(result, Future):
                if result.done():
                    if result.result() is not None:
                        raise ValueError('Expected None, got %r' % result.result())
                    callback()
                else:
                    IOLoop.current().add_future(result, functools.partial(self._when_complete, callback=callback))
            else:
                raise ValueError("Expected Future or None, got %r" % result)
        except Exception as e:
            self._handle_request_exception(e)

    def _execute_method(self):
        if not self._finished:
            method = getattr(self, self.request.method.lower())
            try:
                self.when_response(method(*self.path_args, **self.path_kwargs))
            except Exception as e:
                self.api_exc_info = sys.exc_info()
                self._handle_request_exception(e)

    def _handle_request_exception(self, e):
        if self._finished:
            return
        self.api_exception = e
        if not self.api_exc_info:
            self.api_exc_info = sys.exc_info()
        if isinstance(e, ApiHTTPError):
            self.response(e)
        else:
            self.response(ServerError(e))

    def when_response(self, result):
        try:
            if isinstance(result, Future):
                if result.done():
                    self.response(result.result())
                else:
                    IOLoop.current().add_future(result, self.when_response)
            else:
                self.response(result)
        except Exception as e:
            if isinstance(result, Future):
                self.api_exc_info = result.exc_info()
            else:
                self.api_exc_info = sys.exc_info()
            self._handle_request_exception(e)

    def response(self, result):
        data = self.application.formater(self, result).format()
        self.application.serialize.dumps(self, data)

    def check_etag_header(self):
        return False

    def set_etag_header(self):
        return

    @property
    def current_cursor(self):
        if self._current_cursor is None:
            cursor_id = self.get_query_argument("_c", None)
            if cursor_id:
                self._current_cursor = Cursor.load(cursor_id)
            else:
                self._current_cursor = Cursor(0, '', 1)
        return self._current_cursor