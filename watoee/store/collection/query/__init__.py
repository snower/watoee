# -*- coding: utf-8 -*-
# 15/3/31
# create by: snower

from bson.objectid import ObjectId
from tornado import gen
from ..collection import Collection
from ...utils.query import Query
from ...utils.sort import Sort
from common.exception import NotFoundError
import settings

class QueryCollection(Collection):
    @gen.coroutine
    def query(self, query, skip, limit=settings.PER_PAGE_LIMIT, sort=None):
        query = Query(self, query)
        skip = int(skip)
        limit = int(limit or settings.PER_PAGE_LIMIT)
        sort = Sort(self, sort)

        cursor = self.get_collection().find(query.to_dict())
        if sort:
            cursor.sort(sort.to_dict())
        cursor.skip(skip).limit(limit)
        datas = yield cursor.to_list(limit)
        raise gen.Return(datas)

    @gen.coroutine
    def count(self, query):
        query = Query(self, query)
        cursor = self.get_collection().find(query.to_dict())
        count = yield cursor.count()
        raise gen.Return(count)

    @gen.coroutine
    def query_one(self, objectid):
        obj = yield self.get_collection().find_one({"_id": ObjectId(objectid)})
        if not obj:
            raise NotFoundError(u"对象未找到", 401)
        raise gen.Return(obj)