# -*- coding: utf-8 -*-
# 15/3/31
# create by: snower

from tornado import gen
from user import UserAuth

@gen.coroutine
def auth(auth_type, handler, config):
    raise gen.Return(None)