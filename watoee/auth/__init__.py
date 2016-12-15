# -*- coding: utf-8 -*-
# 15/3/31
# create by: snower

from bson.objectid import ObjectId
from tornado import gen
from common.db import MongoDB
from common.exception import ForbiddenError
import auths

class AppidNotFoundError(ForbiddenError):
    def __init__(self):
        super(AppidNotFoundError, self).__init__(u"appid not found", 301)

class AppkeyError(ForbiddenError):
    def __init__(self):
        super(AppkeyError, self).__init__(u"appkey error", 302)

class AccessTokenError(ForbiddenError):
    def __init__(self):
        super(AccessTokenError, self).__init__(u"access token error", 303)

class EmptyCollectionError(ForbiddenError):
    def __init__(self):
        super(EmptyCollectionError, self).__init__(u"empty collection", 304)

class Config(object):
    db = MongoDB()

    def __init__(self, handler):
        self.handler = handler
        self._access_type = None
        self._appid = None
        self._appkey = None
        self._access_token = None
        self._config = None
        self._readonly = None
        self._writeonly = None
        self._auths = {}

    @property
    def readonly(self):
        return self._readonly

    @property
    def writeonly(self):
        return self._writeonly

    @property
    def name(self):
        return  self._config["name"]

    @property
    def config(self):
        return self._config

    def check_appkey(self):
        if self._appkey:
            if self._config["appkey"] != self._appkey:
                if self._config["read_appkey"] == self._appkey:
                    self._readonly = True
                elif self._config["write_appkey"] == self._appkey:
                    self._writeonly = True
                else:
                    raise AppkeyError()

    @gen.coroutine
    def load_group(self):
        self._config = yield self.db.store['sys.group'].find_one({"appid": self._appid})
        if not self._config:
            raise AppidNotFoundError()
        self.check_appkey()
        yield self.load_collections_by_group()

    @gen.coroutine
    def load_collection(self):
        self._config = yield self.db.store['sys.collection'].find_one({"appid": self._appid})
        if not self._config:
            raise AppidNotFoundError()
        self.check_appkey()
        yield self.collection_auth(self._config)
        yield self.load_collection_group()

    @gen.coroutine
    def load_collections_by_group(self):
        cursor = self.db.store['sys.collection'].find({"group_id":ObjectId(self._config["_id"])})
        collections = yield cursor.to_list(None)
        if not collections:
            raise EmptyCollectionError()
        for collection in collections:
            yield self.collection_auth(collection)
        self._config["collections"] = {collection["name"]:collection for collection in collections}

    @gen.coroutine
    def load_collection_group(self):
        group = yield self.db.store['sys.group'].find_one({"_id": ObjectId(self._config["group_id"])})
        for key, value in group.iteritems():
            if key not in self._config:
                self._config[key] = value
            else:
                if isinstance(value, (list, tuple)):
                    self._config[key] = tuple(set(self._config[key] + value))
                elif isinstance(value, dict):
                    value.update(self._config[key])
                    self._config[key] = value

    @gen.coroutine
    def load(self):
        self._access_type = self.handler.request.headers.get("X-STORE-TYPE", "COLLECTION")
        self._appid = self.handler.request.headers.get("X-STORE-APPID", "")
        self._appkey = self.handler.request.headers.get("X-STORE-APPKEY", "")
        self._access_token = self.handler.request.headers.get("X-STORE-ACCESS-TOKEN", "")

        if self._access_type == "GROUP":
            yield self.load_group()
        else:
            yield self.load_collection()

    @gen.coroutine
    def collection_auth(self, collection_config):
        if collection_config["auth"] not in self._auths:
            auth = yield auths.auth(collection_config["auth"], self.handler, self)
            self._auths[collection_config["auth"]]= auth

    def is_group(self):
        return self._access_type == "GROUP"

    def get_collection(self, name):
        if self.is_group():
            collection_name = ".".join([self.name, name])
            if collection_name in self._config["collections"] and self._config["collections"][collection_name]["access_group"]:
                return self._config["collections"][collection_name]
        else:
            if self.name.endswith(name):
                return self._config
        return None