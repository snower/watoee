# -*- coding: utf-8 -*-
# 15/3/31
# create by: snower

import pytz
import datetime
from tornado import gen
from ..collection import Collection
from ...utils.query import Query
from ...utils.update import Update

class UpdateCollection(Collection):
    def get_default(self, update):
        if "$set" not in update:
            update["$set"] = {}
        if "updated_at" not in update["$set"]:
            update["$set"]["updated_at"] = datetime.datetime.now(pytz.utc)
        return update

    @gen.coroutine
    def update(self, query, update):
        query = Query(self, query)
        update = Update(self, update)

        multi = False if len(query) == 1 and "_id" in query else True

        update = self.get_default(update.to_dict())

        if multi:
            result = yield self.get_collection().update(query.to_dict(), update, multi=True)
        else:
            result = yield self.get_collection().find_and_modify(query.to_dict(), update, new=True, upsert = True)

        raise gen.Return(result)