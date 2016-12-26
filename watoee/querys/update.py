# -*- coding: utf-8 -*-
# 15/4/3
# create by: snower

from common.exception import IllegalError

class Update(object):
    UPDATE_EXPRESSIONS = {"$set": "$set", "$unset": "$unset", "$inc": "$inc"}

    def __init__(self, operation, update):
        self._operation = operation
        self._oupdate = update
        self._update = self.parse(self._oupdate)


    def parse(self, update):
        result = {}
        for expression, value in update.items():
            if expression not in self.UPDATE_EXPRESSIONS:
                try:
                    value = self.format_value(expression, expression, value)
                    if value:
                        if "$set" not in result:
                            result["$set"] = {}
                        result["$set"][expression] = value
                except ValueError as e:
                    IllegalError(e.message, 202)
            else:
                value = self.parse_expression(expression, value)
                if value and isinstance(value, dict):
                    if self.UPDATE_EXPRESSIONS[expression] not in result:
                        result[self.UPDATE_EXPRESSIONS[expression]] = {}
                    result[self.UPDATE_EXPRESSIONS[expression]].update(value)
        return result or None

    def parse_expression(self, expression, values):
        result = {}
        for key, value in values.items():
            try:
                result[key] = self.format_value(key, expression, value)
            except ValueError as e:
                IllegalError(e.message, 202)
        return result

    def format_value(self, key, expression, value):
        return self._operation.validate_field(key, value)

    def to_dict(self):
        return self._update

    def __nonzero__(self):
        return bool(self._update)