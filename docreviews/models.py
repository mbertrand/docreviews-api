# -*- coding: utf-8 -*-
from collections import OrderedDict

from sqlalchemy.orm import validates
from docreviews import db, DocReviewApiException


class Doctor(db.Model):
    """
    Represents a doctor
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))

    def __init__(self, name, id=None):
        self.name = name
        if id:
            self.id = id

    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise DocReviewApiException("Name must not be null")
        return name

    def __repr__(self):
        return "{}:{}".format(self.id, self.name)

    @property
    def parent_json(self):
        return OrderedDict({
            "id": self.id,
            "name": self.name
        })

    @property
    def json(self):
        return OrderedDict({
            "name": self.name,
            "id": self.id,
            "reviews": [review.parent_json for review in self.reviews]
        })


class Review(db.Model):
    """
    Represents a doctor"s review
    """
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    doctor = db.relationship(
        Doctor, backref=db.backref("reviews", cascade="delete, delete-orphan"))

    def __init__(self, description, doctor_id, id=None):
        self.description = description
        self.doctor_id = doctor_id
        if id:
            self.id = id

    def __repr__(self):
        return "{}:{}:{}".format(self.id, self.description, self.doctor)

    @validates("description")
    def validate_description(self, key, description):
        if not description:
            raise DocReviewApiException("Description must not be null")
        return description

    @property
    def parent_json(self):
        return OrderedDict({
            "id": self.id,
            "description": self.description
        })

    @property
    def json(self):
        return OrderedDict({
            "description": self.description,
            "id": self.id,
            "doctor": self.doctor.parent_json
        })