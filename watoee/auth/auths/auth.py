# -*- coding: utf-8 -*-
# 15/4/3
# create by: snower

from tornado import gen
from common.exception import ForbiddenError

class AuthFailError(ForbiddenError):
    def __init__(self, message):
        super(AuthFailError, self).__init__(message, 306)

class Auth(object):
    def __init__(self, handler, config):
        self.handler = handler
        self.config = config

    @gen.coroutine
    def auth(self):
        pass

    def get_default_data(self):
        return {}