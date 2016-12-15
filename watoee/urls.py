# -*- coding: utf-8 -*-
#14-6-28
# create by: snower

from handlers import base
from handlers import handler

urls=(
    (r'^/v1/([a-zA-Z0-9_]+)$', handler.GroupRequestHandler),
    (r'^/v1/([a-zA-Z0-9_]+)/([a-zA-Z0-9_]+)$', handler.CollectionRequestHandler),
    (r'^/v1/([a-zA-Z0-9_]+)/([a-zA-Z0-9_]+)/([0-9a-fA-F]{24})$', handler.ObjectRequestHandler),
    (r'^/', base.RequestHandler),
)