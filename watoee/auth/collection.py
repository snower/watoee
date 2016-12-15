# -*- coding: utf-8 -*-
# 15/3/31
# create by: snower

from tornado import gen
from common.exception import ForbiddenError

class NotAllowAccessError(ForbiddenError):
    def __init__(self):
        super(NotAllowAccessError, self).__init__(u"not allow access", 311)

class CollectionAuth(object):
    def __init__(self, config, group, collection):
        self.config = config
        self.handler = config.handler
        self.group = group
        self.collection = collection

    def is_allow(self):
        if self.config.is_group():
            if not self.config.get_collection(self.collection):
                raise NotAllowAccessError()
        else:
            if ".".join([self.group, self.collection]) != self.config.name:
                raise NotAllowAccessError()

    def is_allow_query(self):
        if self.config._writeonly:
            raise NotAllowAccessError()
        collection = self.config.get_collection(self.collection)
        if "query" not in collection["access"]:
            raise NotAllowAccessError()

    def is_allow_insert(self):
        if self.config._readonly:
            raise NotAllowAccessError()
        collection = self.config.get_collection(self.collection)
        if "insert" not in collection["access"]:
            raise NotAllowAccessError()

    def is_allow_update(self):
        if self.config._readonly:
            raise NotAllowAccessError()
        collection = self.config.get_collection(self.collection)
        if "update" not in collection["access"]:
            raise NotAllowAccessError()

    def is_allow_delete(self):
        if self.config._readonly:
            raise NotAllowAccessError()
        collection = self.config.get_collection(self.collection)
        if "delete" not in collection["access"]:
            raise NotAllowAccessError()

    def get_struct(self):
        collection = self.config.get_collection(self.collection)
        if not collection:
            return {}
        return collection["struct"]

    def get_struct_type(self):
        collection = self.config.get_collection(self.collection)
        if not collection:
            return "normal"
        return collection["struct_type"]

    def get_auth_default_data(self):
        collection = self.config.get_collection(self.collection)
        if collection:
            if self.config._auths[collection["auth"]]:
                return self.config._auths[collection["auth"]].get_default_data()
        return {}