# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from docreviews import config

db = SQLAlchemy()


class DocReviewApiException(Exception):
    code = 400

    def __init__(self, message, code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if code is not None:
            self.code = code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def create_app(config_name, env_settings=None):
    """
    Create the flask app using specified settings
    :param config_name: name of configuration class to use
    :param env_settings: Environmental settings name to use
    :return: app
    """
    app = Flask(__name__)
    app.config.from_object(getattr(config, config_name))

    # Override default settings if applicable
    if env_settings:
        app.config.from_envvar(env_settings, silent=True)

    # Connect the app and db
    db.app = app
    db.init_app(app)
    db.create_all()
    return app


