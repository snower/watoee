# -*- coding: utf-8 -*-
# 2014/7/17
# create by: snower

# -*- coding: utf-8 -*-
# 14-6-28
# create by: snower

import motor


class DataBase(object):
    def __init__(self, db):
        self._db = db

    def __getattr__(self, name):
        collection = self._db[name]
        setattr(self, name, collection)
        return collection

    def __getitem__(self, name):
        return getattr(self, name)

    def command(self, *args, **kwargs):
        return self._db.command(*args, **kwargs)


class MongoDB(object):
    _config = {}
    _conns = {}

    @staticmethod
    def config(config):
        MongoDB._config.update(config)

    @staticmethod
    def load():
        for name, config in MongoDB._config.iteritems():
            if "max_pool_size" not in config:
                config["max_pool_size"] = 256
            if 'waitQueueTimeoutMS' not in config:
                config["waitQueueTimeoutMS"] = 8000

            if "host" in config:
                MongoDB._conns[name] = motor.MotorClient(tz_aware= True, **config)
            else:
                MongoDB._conns[name] = motor.MotorReplicaSetClient(tz_aware=True, read_preference = "secondaryPreferred", **config)

    def __init__(self, db_alias="default"):
        self._db_alias = db_alias
        self._conn = None

    def __getattr__(self, name):
        if self._conn is None:
            self._conn = self._conns[self._db_alias]
        db = DataBase(self._conn[name])
        setattr(self, name, db)
        return db

    def __getitem__(self, name):
        return getattr(self, name)
