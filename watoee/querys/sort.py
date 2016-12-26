# -*- coding: utf-8 -*-
# 15/4/3
# create by: snower

class Sort(object):
    def __init__(self, operation, sort):
        self._operation = operation
        self._osort = sort
        self._sort = self.parse(self._osort)

    def parse(self, sort):
        if isinstance(sort, basestring):
            return ((sort, 1), )

        if isinstance(sort, dict):
            result = []
            for k, s in sort.iteritems():
                result.append((k,  self.get_adsc(s)))
            return result or None
        return None

    def get_adsc(self, adsc):
        if isinstance(adsc, basestring):
            if adsc.isdigit():
                return 1 if int(adsc) > 0 else -1
            return 1 if adsc == "ASC" else -1
        return 1 if int(adsc) > 0 else -1

    def to_dict(self):
        return self._sort

    def __nonzero__(self):
        return bool(self._sort)