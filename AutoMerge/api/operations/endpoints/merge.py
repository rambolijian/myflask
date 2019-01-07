#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
from flask import request, session
from flask_restplus import Resource
from api.operations.business import merge_master_into_release, merge_release_into_master
from api.operations.serializers import merge_api
from api.restplus import api
from database.models import Automerge, HBTC_ENVIRONMENT

log = logging.getLogger("automerge")

ns = api.namespace('merge', description='Operations related to merge branches')


@ns.route('/')
class MergeBranches(Resource):

    @api.response(200, 'Merge successfully.')
    @api.expect(merge_api)
    def post(self):
        """
        Returns list of branches after merging.
        入参：
            {
            "project": "hb_risk",
            "source_branch": "release_2018xxxx",
            "target_branch": "master"
            }
        """
        result = {}
        if not request.json or not 'project' in request.json or not 'source_branch' in request.json or not 'target_branch' in request.json:
            api.abort(404, "projects or source_branch doesn't exist")

        pro = request.json['project']
        source_branch = request.json['source_branch']

        log.info(">>>>> Starting merge: {}: {} <<<<<".format(pro, source_branch))
        if source_branch != "":
            result = merge_release_into_master(pro, source_branch)
        else:
            result = merge_master_into_release(pro)
        log.info(">>>>> Merging result: {} <<<<<".format(result))

        return result, 200
        ## 以下采用session方式和前端进行交互
        # if 'project' in session:
        #     log.info(">>>>> Starting merge: {} <<<<<".format(session['project']))
        #
        #     if session['source_branch'] != "":
        #         result = merge_release_into_master(session['project'], session['source_branch'])
        #     else:
        #         result = merge_master_into_release(session['project'])
        #     log.info(">>>>> Merging result: {} <<<<<".format(result))
        #
        #     return result, 200
        # else:
        #     log.info(">>>>> Starting merge: init <<<<<")
        #
        #     return {}, 200
