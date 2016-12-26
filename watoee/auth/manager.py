# -*- coding: utf-8 -*-
# 16/12/26
# create by: snower

from tornado import gen

class AuthManager(object):
    @gen.coroutine
    def auth(self, auth_type, handler, config):
        raise gen.Return(None)