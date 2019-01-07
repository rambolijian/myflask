#!/usr/bin/python
# -*- coding: UTF-8 -*-

from datetime import datetime
from database import db
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
#
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:HouBank2018aa!@192.168.13.116/qa_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy()
# db.init_app(app)
# db.app = app

class Automerge(db.Model):
    __tablename__ = 'automerge'

    id = db.Column(db.Integer, primary_key=True)
    project = db.Column(db.String(100))
    open = db.Column(db.String(100))
    branch = db.Column(db.String(100))
    result = db.Column(db.String(800))
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

    def __repr__(self):
        return '<Automerge %r>' % self.title

class HBTC_ENVIRONMENT(db.Model):
    __tablename__ = "hbtc_environment"

    id = db.Column(db.Integer, primary_key=True)
    system = db.Column(db.String(200))
    create_time = db.Column(db.DateTime)
    update_time = db.Column(db.DateTime)
    enable = db.Column(db.String(200))
    db_instance = db.Column(db.String(800))
    project_leader_id = db.Column(db.Integer)
    project_name = db.Column(db.String(800))
    dev_group = db.Column(db.String(800))
    order = db.Column(db.Integer)
    build_job = db.Column(db.String(100))
    deploy_job = db.Column(db.String(100))
    git_pro_name = db.Column(db.String(800))

# if __name__ == "__main__":
#     pass
#     db.create_all()
#     HBTC_ENVIRONMENT.query.filter_by(role=git_pro_name).all()
