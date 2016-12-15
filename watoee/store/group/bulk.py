# -*- coding: utf-8 -*-
# 15/3/31
# create by: snower

from tornado import gen
from common.exception import ForbiddenError
from ..collection.query import QueryCollection
from ..collection.insert import InsertCollection
from ..collection.update import UpdateCollection
from ..collection.delete import DeleteCollection
from auth.collection import CollectionAuth

class BulkOperation(object):
    def __init__(self, handler, auth, group):
        self.handler = handler
        self.auth = auth
        self.group = group

    @gen.coroutine
    def bulk(self, requests):
        results = []
        safe = requests.get("safe", False)
        for request in requests["requests"]:
            try:
                result = yield self.request(request)
                results.append(self.handler.get_response_result(result))
            except Exception as e:
                result = e
                results.append(self.handler.get_response_result(result))
                if safe:break
        raise gen.Return(results)

    @gen.coroutine
    def request(self, request):
        collection, objectid = self.parse_url(request["path"])
        request["method"] = request["method"].lower()
        if objectid:
            result = yield self.object_request(request, collection, objectid)
        else:
            result = yield self.collection_request(request, collection)
        raise gen.Return(result)

    @gen.coroutine
    def collection_request(self, request, collection):
        if request["method"] == "get":
            raise ForbiddenError(u"未知操作", 322)
        elif request["method"] == "post":
            auth = CollectionAuth(self.auth.config, self.group, collection)
            insert = InsertCollection(self.handler, auth, self.group, collection)
            result = yield insert.insert(request["body"])
            raise gen.Return(result)
        elif request["method"] == "put":
            auth = CollectionAuth(self.auth.config, self.group, collection)
            update = UpdateCollection(self.handler, auth, self.group, collection)
            result = yield update.update(request["query"], request["body"])
            raise gen.Return(result)
        elif request["method"] == "delete":
            auth = CollectionAuth(self.auth.config, self.group, collection)
            delete = DeleteCollection(self.handler, auth, self.group, collection)
            result = yield delete.delete(request["query"])
            raise gen.Return(result)
        else:
            raise ForbiddenError(u"未知操作", 322)

    @gen.coroutine
    def object_request(self, request, collection, objectid):
        if request["method"] == "get":
            auth = CollectionAuth(self.auth.config, self.group, collection)
            query = QueryCollection(self.handler, auth, self.group, collection)
            result = yield query.query_one(objectid)
            raise gen.Return(result)
        elif request["method"] == "post" or request["method"] == "put":
            auth = CollectionAuth(self.auth.config, self.group, collection)
            update = UpdateCollection(self.handler, auth, self.group, collection)
            result = yield update.update({"_id": objectid}, request["body"])
            raise gen.Return(result)
        elif request["method"] == "delete":
            auth = CollectionAuth(self.auth.config, self.group, collection)
            delete = DeleteCollection(self.handler, auth, self.group, collection)
            result = yield delete.delete({"_id": objectid})
            raise gen.Return(result)
        else:
            raise ForbiddenError(u"未知操作", 322)

    def parse_url(self, url):
        urls = url.split("/")
        if len(urls) == 2:
            raise ForbiddenError(u"未知操作", 320)
        if urls[-2] != self.group:
                raise ForbiddenError(u"不相同的组", 321)
        if len(urls) == 3:
            return urls[-1], None
        else:
            return urls[-2], urls[-1]