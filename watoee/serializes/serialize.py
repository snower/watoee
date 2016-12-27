# -*- coding: utf-8 -*-
# 16/12/26
# create by: snower

class Serialize(object):
    def __init__(self, handler, data):
        self.handler = handler
        self.data = data

    def dumps(self):
        raise NotImplementedError()