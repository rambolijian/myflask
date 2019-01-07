#!/usr/bin/python
# -*- coding: UTF-8 -*-

from flask_restplus import reqparse

compare_arguments = reqparse.RequestParser()
compare_arguments.add_argument('projects', type=str, required=True, help='Projects')
compare_arguments.add_argument('force', type=bool, required=True, help='Compare master or release branch')
