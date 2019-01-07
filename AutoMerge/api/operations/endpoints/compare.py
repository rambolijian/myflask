#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging

from flask import request
from flask_restplus import Resource
from api.operations.business import comparing_all_projects
from api.operations.serializers import compare_api
from api.operations.parsers import compare_arguments
from api.restplus import api
from database.models import Automerge, HBTC_ENVIRONMENT

log = logging.getLogger("automerge")

ns = api.namespace('compare', description='Operations related to compare branches')


@ns.route('/')
class CompareCollection(Resource):

    @api.response(200, 'Compare successfully.')
    @api.expect(compare_api)
    # @api.marshal_with(compare_api)
    def post(self):
        """
        Returns list of project compares.
        入参：
            {
            "projects": "['hb_risk']",
            "force": "false"
            }
        """
        if not request.json or not 'projects' in request.json or not 'force' in request.json:
            api.abort(404, "projects or force doesn't exist")

        force = request.json['force']
        log.info(">>>>> Comparing: {} <<<<<".format(request.json['projects']))
        response = comparing_all_projects(eval(request.json['projects']), force)
        log.info(">>>>> Compare result: {} <<<<<".format(response))
        force = {"force": force}
        response[0].update(force)
        return response[0], 200