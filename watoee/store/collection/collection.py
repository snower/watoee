# -*- coding: utf-8 -*-
# 15/4/1
# create by: snower

from bson.objectid import ObjectId
from common.db import MongoDB

class Collection(object):
    db = MongoDB()

    def __init__(self, handler, auth, group, collection):
        self.handler = handler
        self.auth = auth
        self.group = group
        self.collection = collection
        self.struct_type = self.auth.get_struct_type()
        self.struct = self.auth.get_struct()

    def get_collection(self):
        return self.db.store["%s.%s" % (self.group, self.collection)]

    def validate_field(self, key, value):
        if not isinstance(value, (basestring, int, float, long, bool, list, tuple, set, dict)):
            raise ValueError(u"value error")

        if key == "_id":
            return ObjectId(value)

        if key not in self.struct:
            return value

        if self.struct[key] in "int":
            return int(value)
        elif self.struct[key] == "float":
            return float(value)
        elif self.struct[key] == "objectid":
            return ObjectId(value)
        return value