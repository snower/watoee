# -*- coding: utf-8 -*-
# 15/3/31
# create by: snower

from tornado import gen
from ..collection import Collection
from ...utils.query import Query

class DeleteCollection(Collection):
    @gen.coroutine
    def delete(self, query):
        query = Query(self, query)

        result = yield self.get_collection().remove(query.to_dict())

        raise gen.Return(result)