# -*- coding: utf-8 -*-
# 16/12/15
# create by: snower

class Cursor(object):
    def __init__(self, page, _id, direction):
        self.page, self._id, self.direction = page, _id, (1 if int(direction) > 0 else -1)
        if self.page < 0:
            self.page = 0
        if isinstance(self._id, ObjectId):
            self._id = self._id.binary
        elif len(self._id) == 24:
            self._id = self._id.decode("hex")

    @classmethod
    def load(cls, cursor_id):
        return Cursor(*struct.unpack("!I12sb", cursor_id.decode("hex")))

    def __str__(self):
        return struct.pack("!I12sb", self.page, self._id, self.direction).encode("hex")

    def next(self, data):
        return Cursor(self.page + 1, data[-1]["_id"], 1) if data else self

    def previous(self, data):
        return Cursor(self.page - 1, data[0]["_id"], -1) if data else self

    def __call__(self, result, data):
        result["previous_cursor"] = str(self.previous(data))
        result["next_cursor"] = str(self.next(data))
        return result