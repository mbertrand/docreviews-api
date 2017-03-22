# -*- coding: utf-8 -*-

import argparse
from flask import jsonify, request, abort
from docreviews.models import Doctor, Review
from docreviews import create_app, db, DocReviewApiException


def create_api(app):
    """
    Set up the API endpoints.
    """

    @app.errorhandler(DocReviewApiException)
    def handle_invalid_usage(error):
        """
        Create and return a JSON-ified error message
        :param error: Error to jsonify
        :return: error message in JSON format
        """
        response = jsonify(error.to_dict())
        response.status_code = error.code
        return response

    @app.route('/', methods=['GET'])
    def root():
        """
        Give the user some URL suggestions
        """
        return jsonify({
            "message": "Try /doctors or /reviews"
        })

    @app.route('/doctors', methods=['GET'])
    def doctor_list():
        """
        Return a list of all doctors
        :return: Doctors as JSON
        TODO: Create a max amount of doctors to return, use paging
        """
        return jsonify({'doctors': [doc.json for doc in Doctor.query.all()]})

    @app.route('/doctors/<int:id>', methods=['GET'])
    def get_doctor(id):
        """
        Get a doctor by id number.
        Make sure id is indexed in database for production.
        :param id: ID of doctor
        :return: Doctor as JSON
        """
        doc = Doctor.query.get(id)
        if not doc:
            return jsonify({}), 201
        return jsonify(doc.json), 201

    @app.route('/doctors/<int:doc_id>/reviews/<int:review_id>', methods=['GET'])
    def get_doctor_review(doc_id, review_id):
        """
        Get a particular review of a particular doctor.  Raise an exception
        if the review doesn't belong to that doctor.
        :param doc_id: Doctor ID
        :param review_id: Review ID
        :return: Review as JSON
        """
        review = Review.query.get(review_id)
        if not review:
            return jsonify({}), 201
        if review.doctor_id != doc_id:
            raise DocReviewApiException("Doctor and Review mismatch")
        return jsonify(review.json), 201

    @app.route('/doctors', methods=['POST'])
    def add_doctor():
        """
        Add a doctor to the database.
        :return: Doctor as JSON
        """
        if not request.json:
            abort(400)
        if "name" not in request.json:
            raise DocReviewApiException("'name' is required")
        doc = Doctor(request.json["name"])
        db.session.add(doc)
        db.session.commit()
        return jsonify(doc.json), 201

    @app.route('/doctors/<int:id>', methods=['PATCH'])
    def update_doctor(id):
        """
        Update the name of a doctor.
        :param id: Doctor ID
        :return: Doctor as JSON
        """
        doc = Doctor.query.get(id)
        if not doc:
            abort(400)
        for attribute in request.json:
            if attribute != "name":
                raise DocReviewApiException(
                    "Only doctor name can be modified", code=400)
        for attribute in request.json:
            setattr(doc, attribute, request.json[attribute])
        db.session.add(doc)
        db.session.commit()
        return jsonify(doc.json), 201

    @app.route('/doctors/<int:id>', methods=['DELETE'])
    def delete_doctor(id):
        """
        Delete a doctor from the database
        :param id: Doctor ID
        :return: Empty JSON
        """
        doc = Doctor.query.get(id)
        db.session.delete(doc)
        db.session.commit()
        return jsonify(), 204

    @app.route('/reviews', methods=['GET'])
    def review_list():
        """
        Get a list of all reviews in the database.
        :return: Reviews as JSON
        TODO: Create a max amount of reviews to return, use paging
        """
        return jsonify({'reviews': [rev.json for rev in Review.query.all()]})

    @app.route('/reviews/<int:id>', methods=['GET'])
    def get_review(id):
        """
        Get a review by id
        :param id: Review ID
        :return: Review as JSON
        """
        review = Review.query.get(id)
        if not review:
            return jsonify({}), 201
        return jsonify(review.json), 201

    @app.route('/reviews', methods=['POST'])
    def add_review():
        """
        Add a new review to the database
        :return: Review as JSON
        """
        if not request.json:
            abort(400)
        attrs = []
        for attribute in ("description", "doctor_id"):
            if attribute not in request.json:
                attrs.append(attribute)
        if attrs:
            raise DocReviewApiException("Required: {}".format(", ".join(attrs)))

        doc_id = request.json["doctor_id"]
        doctor = Doctor.query.get(doc_id)
        if not doctor:
            raise DocReviewApiException(
                "Doctor does not exist with id: {}".format(doc_id))

        review = Review(request.json["description"], request.json["doctor_id"])
        db.session.add(review)
        db.session.commit()
        return jsonify(review.json), 201

    @app.route('/reviews/<int:id>', methods=['PATCH'])
    def update_review(id):
        """
        Update the description of a review
        :param id: Review ID
        :return: Empty JSON
        """
        review = Review.query.get(id)
        if not review:
            abort(400)
        for attribute in request.json:
            if attribute != "description":
                raise DocReviewApiException(
                    "Only review description can be modified", code=400)
        review.description = request.json["description"]
        db.session.add(review)
        db.session.commit()
        return jsonify(review.json), 201

    @app.route('/reviews/<int:id>', methods=['DELETE'])
    def delete_review(id):
        """
        Delete a review from the database
        :param id: Review ID
        :return: Empty JSON
        """
        review = Review.query.get(id)
        db.session.delete(review)
        db.session.commit()
        return jsonify(), 204


if __name__ == "__main__":

    # Set runtime options based on commandline parameters if any
    parser = argparse.ArgumentParser()
    parser.add_argument("--host",
                        help="Host to run on",
                        default="0.0.0.0")
    parser.add_argument("--port",
                        help="Port to run on",
                        type=int,
                        default=5000)
    parser.add_argument("--nodebug",
                        dest="debug",
                        help="Non-debug mode",
                        default=True,
                        action="store_false")
    parser.add_argument("--config",
                        help="Configuration to use",
                        default="DefaultSettings")
    parser.add_argument("--env_config",
                        help="Environment setting to use for config file",
                        default=None)
    args = parser.parse_args()

    # Create and run the flask app
    app = create_app(args.config, args.env_config)
    create_api(app)
    app.run(debug=args.debug, host=args.host, port=args.port)