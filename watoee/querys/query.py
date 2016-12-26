# -*- coding: utf-8 -*-
# 15/4/3
# create by: snower

import datetime
from bson.objectid import ObjectId
from bson.timestamp import Timestamp

class Query(object):
    QUERY_EXPRESSIONS = {'$in': '$in', '$gt': '$gt', '$gte': '$gte', '$lt': '$lt', '$lte': '$lte', '$eq': '$eq', '$ne': '$ne'}

    def __init__(self, operation, query):
        self._operation = operation
        self._oquery = query
        self._query = self.parse(self._oquery)

    def allow_type(self, value):
      return isinstance(value, (basestring, int, float, long, bool, datetime.date, datetime.datetime, datetime.time, ObjectId, Timestamp)) or value is None

    def parse(self, query):
        for key, value in query.items():
            operation = self.parse_expression(key, value)
            if not operation:
                query.pop(key)
            else:
                query[key] = operation
        return query or None

    def parse_expression(self, key, expressions):
        if not isinstance(expressions, dict):
            try:
                value = self.format_value(key, '', expressions)
                if not self.allow_type(value):
                    return None
                return value
            except ValueError as e:
                return None

        result = {}
        for expression, value in expressions.items():
            if expression in self.QUERY_EXPRESSIONS:
                try:
                    value = self.format_value(key, expression, value)
                    if self.allow_type(value):
                        result[self.QUERY_EXPRESSIONS[expression]] = self.format_value(key, expression, value)
                except ValueError as e:
                    pass
        return result

    def format_value(self, key, expression, value):
        if expression == 'in':
            value = [_v for _v in value if self._operation.validate_field(key, value)]
            if value:
                return value
            raise ValueError()
        else:
            return self._operation.validate_field(key, value)

    def to_dict(self):
        return self._query

    def __nonzero__(self):
        return bool(self._query)

    def __len__(self):
        return len(self._query) if self._query else 0

    def __contains__(self, item):
        return (item in self._query) if self._query else False
