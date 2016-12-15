# -*- coding: utf-8 -*-
# 15/3/31
# create by: snower

from common.exception import ForbiddenError

class NotAllowAccessError(ForbiddenError):
    def __init__(self):
        super(NotAllowAccessError, self).__init__(u"not allow access", 311)

class GroupAuth(object):
    def __init__(self, config):
        self.config = config
        self.handler = config.handler

    def is_allow(self):
        if not self.config.is_group():
            raise NotAllowAccessError()