#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging.config

import os
from flask import Flask, Blueprint, render_template, session, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
import settings
from api.operations.endpoints.compare import ns as compare_namespace
from api.operations.endpoints.merge import ns as merge_namespace
from api.restplus import api
from database import db
from database.models import Automerge, HBTC_ENVIRONMENT
from api.operations.business import get_all_projects_from_hbtc

app = Flask(__name__)
logging_conf_path = os.path.normpath(os.path.join(os.path.dirname(__file__), './logging.conf'))
logging.config.fileConfig(logging_conf_path)
log = logging.getLogger("automerge")


def configure_app(flask_app):
    flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTPLUS_ERROR_404_HELP
    flask_app.config['SECRET_KEY'] = settings.SECRET_KEY
    log.info(">>>>> Upload configurations completely <<<<<")

def initialize_app(flask_app):
    configure_app(flask_app)

    bootstrap = Bootstrap(app)
    moment = Moment(app)

    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(compare_namespace)
    api.add_namespace(merge_namespace)
    flask_app.register_blueprint(blueprint)

    db.init_app(flask_app)
    log.info(">>>>> Initialize app completely <<<<<")
    db.app = flask_app  #需要重新将app对象赋予db.app，否则会报错
    db.create_all()
    log.info(">>>>> Initialize DB completely <<<<<")
    log.info(">>>>> Initialize completely <<<<<")

def get_project_list():
    project_list = get_all_projects_from_hbtc()
    project_list2 = [("", "")]

    for pro in project_list:
        project_list2.append((pro, pro))
    return project_list2

class NameForm(FlaskForm):
    project = SelectField(
        label="Project",
        validators=[DataRequired("请选择项目")],
        # description="Project",
        coerce=str,
        choices=get_project_list(),
        # choices=[("", ""), ("AutoMerge", "AutoMerge"), ("hb_risk", "hb_risk")],
        render_kw={"class": "form-control"})
    source_branch = StringField('Release Branch', description="Source branch")
    target_branch = SelectField(
        label="Master",
        validators=[DataRequired("请选择master分支")],
        description="Target branch",
        coerce=str,
        choices=[("master", "master")],
        render_kw={"class": "form-control"})
    submit = SubmitField('Merge')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('project')
        if old_name is not None and old_name != form.project.data:
            flash('Looks like you have changed your project!')
        session['project'] = form.project.data
        session['source_branch'] = form.source_branch.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form)

def main():
    initialize_app(app)
    log.info('>>>>> Starting development server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(debug=settings.FLASK_DEBUG)


if __name__ == "__main__":
    main()
