# -*- coding: utf-8 -*-
# 15/3/31
# create by: snower

import json
from tornado import gen
from .handler import RequestHandler
from auth.collection import CollectionAuth
from auth.group import GroupAuth
from store.collection.query import QueryCollection
from store.collection.insert import InsertCollection
from store.collection.update import UpdateCollection
from store.collection.delete import DeleteCollection
from store.group.bulk import BulkOperation
import settings

def format_sort(s):
    if not s:
        return {}
    try:
        return json.loads(s)
    except Exception as e:
        if s[0] not in ("[", "{"):
            return s
        raise


class GroupRequestHandler(RequestHandler):
    @gen.coroutine
    def auth(self):
        auth = GroupAuth(self._auth_config)
        auth.is_allow()
        raise gen.Return(auth)

    @gen.coroutine
    def post(self, group):
        auth = yield self.auth()
        bulk = BulkOperation(self, auth, group)
        datas = yield bulk.bulk(self.request.body_arguments)
        raise gen.Return(datas)

    @gen.coroutine
    def put(self, group):
        auth = yield self.auth()
        bulk = BulkOperation(self, auth, group)
        datas = yield bulk.bulk(self.request.body_arguments)
        raise gen.Return(datas)

class CollectionRequestHandler(RequestHandler):
    @gen.coroutine
    def auth(self, group, collection):
        auth = CollectionAuth(self._auth_config, group, collection)
        auth.is_allow()
        raise gen.Return(auth)

    @gen.coroutine
    def head(self, group, collection):
        auth = yield self.auth(group, collection)
        auth.is_allow_query()

        q = self.get_query_argument("query", {}, format=json.loads)
        query = QueryCollection(self, auth, group, collection)
        count = yield query.count(q)
        raise gen.Return({
            "count": count,
        })

    @gen.coroutine
    def get(self, group, collection):
        auth = yield self.auth(group, collection)
        auth.is_allow_query()

        cursor = self.current_cursor

        q = self.get_query_argument("query", {}, format=json.loads)
        skip = self.get_query_argument("skip", 0, format=int)
        limit = self.get_query_argument("limit", 0, format=int)
        sort = self.get_query_argument("sort", {}, format=format_sort)

        query = QueryCollection(self, auth, group, collection)
        datas = yield query.query(q, skip or (cursor.page * settings.PER_PAGE_LIMIT) or 0, limit or settings.PER_PAGE_LIMIT, sort)
        raise gen.Return(cursor({"result":datas}, datas))

    @gen.coroutine
    def post(self, group, collection):
        auth = yield self.auth(group, collection)
        auth.is_allow_insert()

        insert = InsertCollection(self, auth, group, collection)
        data = yield insert.insert(self.request.body_arguments)
        raise gen.Return(data)

    @gen.coroutine
    def put(self, group, collection):
        auth = yield self.auth(group, collection)
        auth.is_allow_update()

        q = self.get_query_argument("query", {}, format=json.loads)
        q = json.loads(q)

        update = UpdateCollection(self, auth, group, collection)
        data = yield update.update(q, self.request.body_arguments)
        raise gen.Return(data)

    @gen.coroutine
    def delete(self, group, collection):
        auth = yield self.auth(group, collection)
        auth.is_allow_delete()

        q = self.get_query_argument("query", {}, format=json.loads)
        q = json.loads(q)

        delete = DeleteCollection(self, auth, group, collection)
        data = yield delete.delete(q)
        raise gen.Return(data)

class ObjectRequestHandler(RequestHandler):
    @gen.coroutine
    def auth(self, group, collection):
        auth = CollectionAuth(self._auth_config, group, collection)
        auth.is_allow()
        raise gen.Return(auth)

    @gen.coroutine
    def head(self, group, collection, objectid):
        auth = yield self.auth(group, collection)
        auth.is_allow_query()

        query = QueryCollection(self, auth, group, collection)
        yield query.query_one(objectid)

        raise gen.Return({})

    @gen.coroutine
    def get(self, group, collection, objectid):
        auth = yield self.auth(group, collection)
        auth.is_allow_query()

        query = QueryCollection(self, auth, group, collection)
        data = yield query.query_one(objectid)
        raise gen.Return(data)

    @gen.coroutine
    def post(self, group, collection, objectid):
        auth = yield self.auth(group, collection)
        auth.is_allow_update()

        update = UpdateCollection(self, auth, group, collection)
        data = yield update.update({"_id": objectid}, self.request.body_arguments)
        raise gen.Return(data)

    @gen.coroutine
    def put(self, group, collection, objectid):
        auth = yield self.auth(group, collection)
        auth.is_allow_update()

        update = UpdateCollection(self, auth, group, collection)
        data = yield update.update({"_id": objectid}, self.request.body_arguments)
        raise gen.Return(data)

    @gen.coroutine
    def delete(self, group, collection, objectid):
        auth = yield self.auth(group, collection)
        auth.is_allow_delete()

        delete = DeleteCollection(self, auth, group, collection)
        data = yield delete.delete({"_id": objectid})
        raise gen.Return(data)