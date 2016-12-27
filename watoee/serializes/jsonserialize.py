# -*- coding: utf-8 -*-
# 16/12/26
# create by: snower

import json
from .serialize import Serialize

class JsonSerialize(Serialize):
    def dumps(self):
        self.handler.set_header("Content-Type", "application/json; charset=UTF-8")
        if self.handler.request.method == "HEAD":
            for key, value in self.data.iteritems():
                self.handler.set_header("X-STORE-" + key.upper(), value.encode("utf-8") if isinstance(value, unicode) else str(value))
            self.handler.finish('')
        else:
            data = json.dumps(self.data, default=str, ensure_ascii=False).encode("utf-8")
            self.handler.finish(data)