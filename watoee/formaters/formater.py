# -*- coding: utf-8 -*-
# 16/12/26
# create by: snower

from tornado.web import httputil
from ..exceptions import ApiHTTPError

class Formater(object):
    def __init__(self, handler, result):
        self.handler = handler
        self.result = result

    def format(self):
        data = self.result if not isinstance(self.result, ApiHTTPError) else {}
        result = {
            "error_code": 0 if not isinstance(self.result, ApiHTTPError) else self.result.status_code,
            "error_msg": '' if not isinstance(self.result, ApiHTTPError) else self.result.log_message or
                                                                         httputil.responses.get(self.result.status_code, 'Unknown'),
        }
        if isinstance(data, dict):
            result.update(data)
        else:
            result["result"] = data
        return result
