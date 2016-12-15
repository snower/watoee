# -*- coding: utf-8 -*-
# 15/3/31
# create by: snower

import pytz
import datetime
from pymongo.errors import DuplicateKeyError
from tornado import gen
from ..collection import Collection
from common.exception import IllegalError

class DuplicateKeyIllegalError(IllegalError):
    def __init__(self, message):
        super(DuplicateKeyIllegalError, self).__init__(message, 210)

class InsertCollection(Collection):
    def get_default(self, data):
        d = {
            "created_at": datetime.datetime.now(pytz.utc),
            "updated_at": datetime.datetime.now(pytz.utc),
        }
        d.update(self.auth.get_auth_default_data())
        d.update(data)
        return d

    @gen.coroutine
    def insert(self, data):
        if isinstance(data, (tuple, list)):
            result = yield self.insert_many(data)
        else:
            result = yield self.insert_one(data)
        raise gen.Return(result)

    @gen.coroutine
    def insert_one(self, data):
        data = self.validate(data)
        data = self.get_default(data)
        try:
            yield self.get_collection().insert(data)
        except DuplicateKeyError as e:
            raise DuplicateKeyIllegalError(e.message)
        raise gen.Return(data)

    @gen.coroutine
    def insert_many(self, datas):
        results = []
        for data in datas:
            data = self.validate(data)
            data = self.get_default(data)
            results.append(data)
        try:
            yield self.get_collection().insert(results)
        except DuplicateKeyError as e:
            raise DuplicateKeyIllegalError(e.message)
        raise gen.Return(results)

    def validate(self, data):
        for key, value in data.items():
            try:
                data[key] = self.validate_field(key, value)
            except Exception as e:
                raise IllegalError(e.message, 202)
        return data