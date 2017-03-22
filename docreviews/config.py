# -*- coding: utf-8 -*-


class DefaultSettings(object):
    """
    Default settings for the Flask app go here.
    """

    SQLALCHEMY_DATABASE_URI = "sqlite:///docreviews.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Sample Postgres URI
    #SQLALCHEMY_DATABASE_URI = "postgresql://user:password@localhost/caredash"


class TestSettings(object):
    """
    Test settings for the Flask app go here.
    """

    SQLALCHEMY_DATABASE_URI = "sqlite:///docreviewstest.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True
