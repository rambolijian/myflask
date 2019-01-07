#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Flask settings
FLASK_SERVER_NAME = '127.0.0.1:8888'
# FLASK_SERVER_NAME = '10.5.32.13:8888'
FLASK_DEBUG = True  # Do not use debug mode in production

#secret key
SECRET_KEY = 'Welcome to use automerge'

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# SQLAlchemy settings
# SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
# SQLALCHEMY_TRACK_MODIFICATIONS = False

# SQLAlchemy settings
SQLALCHEMY_DATABASE_URI = 'mysql://root:***2018aa!@192.168.13.116/qa_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# gitlab access info
GITLAB_HOST = 'https://code.***.net/'
# my account token
# GITLAB_TOKEN = 'UifdHbUH-jggx7XhG2Do'
#automerge account token
GITLAB_TOKEN = 'Y27VuJvXkRwTwVyydRHK'

# HBTC DB info
DB_HOST = "192.168.13.116"
# DB_NAME = "qa_hbtc"
DB_NAME = "qa_db"
DB_USER = "root"
DB_PASSWORD = "******2018aa!"
