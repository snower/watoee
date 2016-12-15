# -*- coding: utf-8 -*-
# 16/12/15
# create by: snower

from tornado.web import HTTPError

class ApiHTTPError(HTTPError):
    def __init__(self, status_code, log_message, data = {}, *args, **kwargs):
        super(ApiHTTPError,self).__init__(status_code, log_message, *args, **kwargs)

        self.data = data


class IllegalError(ApiHTTPError):
    def __init__(self, log_message, status_code=200, data = {}, *args, **kwargs):
        super(IllegalError,self).__init__(status_code, log_message, *args, **kwargs)

class ForbiddenError(ApiHTTPError):
    def __init__(self, log_message, status_code=300, data = {},  *args, **kwargs):
        super(ForbiddenError,self).__init__(status_code, log_message, *args, **kwargs)

class NotFoundError(ApiHTTPError):
    def __init__(self, log_message, status_code=400, data = {}, *args, **kwargs):
        super(NotFoundError,self).__init__(status_code, log_message, *args, **kwargs)


if True:
    class ServerError(ApiHTTPError):
        def __init__(self, log_message, status_code=500, data = {}, *args, **kwargs):
            if not isinstance(log_message, basestring):
                log_message = log_message.__str__() if isinstance(log_message, HTTPError) else repr(log_message)
            super(ServerError,self).__init__(status_code, log_message, *args, **kwargs)
else:
    class ServerError(ApiHTTPError):
        def __init__(self, log_message, status_code=500 ,data = {}, *args, **kwargs):
            if not isinstance(log_message, basestring):
                log_message = u'服务器错误'
            super(ServerError, self).__init__(status_code, log_message, *args, **kwargs)
