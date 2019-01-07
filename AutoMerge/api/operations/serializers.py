#!/usr/bin/python
# -*- coding: UTF-8 -*-
from flask_restplus import fields
from api.restplus import api

compare_api = api.model('Compare branches', {
    'projects': fields.String(description='Compare which projects'),
    'force': fields.Boolean(description='Compare master or release')
})

merge_release_response_model = api.model('Merging Response', {
    'release_2018xxx1': fields.String(description='Merge which branch'),
    'release_2018xxx2': fields.String(description='Merge which branch')
})

merge_api = api.model('Merge branches', {
    'project': fields.String(description='Merge which project'),
    'opened': fields.String(description='Merge which project'),
    'result': fields.Nested(merge_release_response_model)
})