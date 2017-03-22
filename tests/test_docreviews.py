import json
import unittest
from docreviews import create_app, models
from docreviews.api import create_api, db
from builtins import str

from docreviews.models import Doctor, Review


class DocReviewsTestCase(unittest.TestCase):

    def create_sample_data(self):
        """
        Create sample data for tests: 2 doctors, 1 with 2 reviews, 1 with none
        """
        doctor1 = models.Doctor(name="Doctor Strange", id=1)
        doctor2 = models.Doctor(name="Doctor Who", id=2)
        db.session.add(doctor1)
        db.session.add(doctor2)
        db.session.commit()
        review1 = models.Review(
            description="A nice but strange doctor", doctor_id=1)
        review2 = models.Review(
            description="Cured me of everything, A++", doctor_id=1
        )
        db.session.add(review1)
        db.session.add(review2)
        db.session.commit()

    def setUp(self):
        """
        Create the flask app using test settings
        """
        app = create_app("TestSettings")
        create_api(app)
        self.app = app.test_client()
        self.db = db
        self.create_sample_data()

    def tearDown(self):
        """
        Remove test data
        """
        self.db.session.remove()
        self.db.drop_all()

    def test_add_doctor(self):
        """
        Test that a doctor can be created through the API
        """
        header = {"Content-Type": "application/json"}
        data = json.dumps({"name": "Doctor Doolittle"})
        rv = self.app.post("/doctors", data=data, headers=header)
        self.assertTrue(b"name" in rv.data, rv.data)
        self.assertTrue(b"id" in rv.data, rv.data)

    def test_add_review(self):
        """
        Test that a review can be created through the API
        """
        header = {"Content-Type": "application/json"}
        data = json.dumps({"name": "Doctor Doolittle"})
        response = self.app.post("/doctors", data=data, headers=header)
        doctor = json.loads(str(response.data, "utf-8"))
        data = json.dumps({"description": "Nice doctor",
                           "doctor_id": doctor["id"]})
        response = self.app.post("/reviews", data=data, headers=header)
        review = json.loads(str(response.data, "utf-8"))
        self.assertTrue("description" in review)
        self.assertTrue("doctor" in review)
        self.assertTrue("name" in review["doctor"])

    def test_get_doctor(self):
        """
        Retrieve a doctor by id and verify JSON result
        """
        response = self.app.get("/doctors/1")
        rjson = json.loads(str(response.data, "utf-8"))
        self.assertEquals("Doctor Strange", rjson["name"])
        self.assertEquals(1, rjson["id"])
        self.assertEquals(2, len(rjson["reviews"]))

    def test_delete_doctor(self):
        """
        Delete a doctor by id and verify it's no longer in the database
        """
        response = self.app.delete("/doctors/1")
        self.assertEqual(response.status, "204 NO CONTENT")
        self.assertIsNone(Doctor.query.get(1))

    def test_patch_doctor(self):
        """
        Update a doctor's name by id and verify JSON result
        """
        header = {"Content-Type": "application/json"}
        data = json.dumps({"name": "Doctor Strangelove"})
        response = self.app.patch("/doctors/1", data=data, headers=header)
        rjson = json.loads(str(response.data, "utf-8"))
        self.assertEquals("Doctor Strangelove", rjson["name"])

    def test_get_review(self):
        """
        Retrieve a review by id and verify JSON result
        """
        response = self.app.get("/reviews/1")
        rjson = json.loads(str(response.data, "utf-8"))
        self.assertEquals("Doctor Strange", rjson["doctor"]["name"])
        self.assertEquals("A nice but strange doctor", rjson["description"])

    def test_get_doctor_review(self):
        """
        Retrieve a review by both doctor and review id and verify JSON result
        """
        response = self.app.get("/doctors/1/reviews/2")
        rjson = json.loads(str(response.data, "utf-8"))
        self.assertEquals("Doctor Strange", rjson["doctor"]["name"])
        self.assertEquals("Cured me of everything, A++", rjson["description"])

    def test_get_all_doctors(self):
        """
        Retrieve all doctors in database and verify results
        """
        response = self.app.get("/doctors")
        rjson = json.loads(str(response.data, "utf-8"))
        self.assertEquals(2, len(rjson["doctors"]), rjson)
        for doctor in rjson["doctors"]:
            self.assertTrue("reviews" in doctor, doctor)

    def test_get_all_reviews(self):
        """
        Retrieve all reviews in database and verify results
        :return:
        """
        response = self.app.get("/reviews")
        rjson = json.loads(str(response.data, "utf-8"))
        self.assertEquals(2, len(rjson["reviews"]), rjson)
        for review in rjson["reviews"]:
            self.assertEquals("Doctor Strange", review["doctor"]["name"])
            self.assertTrue("description" in review)

    def test_delete_review(self):
        """
        Delete a doctor by id and verify it's no longer in the database
        """
        response = self.app.delete("/reviews/1")
        self.assertEqual(response.status, "204 NO CONTENT")
        self.assertIsNone(Review.query.get(1))

    def test_patch_review(self):
        """
        Update a doctor's name by id and verify JSON result
        """
        header = {"Content-Type": "application/json"}
        data = json.dumps({"description": "Best doctor ever"})
        response = self.app.patch("/reviews/1", data=data, headers=header)
        rjson = json.loads(str(response.data, "utf-8"))
        self.assertEquals("Best doctor ever", rjson["description"])

    def test_post_bad_doctor(self):
        """
        Try to add a doctor with incorrect fields
        """
        header = {"Content-Type": "application/json"}
        data = json.dumps({"doctor_name": "Doctor Doolittle"})
        response = self.app.post("/doctors", data=data, headers=header)
        rjson = json.loads(str(response.data, "utf-8"))
        self.assertTrue(response.status, 400)
        self.assertEquals(rjson["message"], "'name' is required")

    def test_post_bad_review(self):
        """
        Try to add a review with incorrect fields
        """
        header = {"Content-Type": "application/json"}
        data = json.dumps({"desc": "A great doctor", "doc_id": 1})
        response = self.app.post("/reviews", data=data, headers=header)
        rjson = json.loads(str(response.data, "utf-8"))
        self.assertTrue(response.status, 400)
        self.assertEquals(rjson["message"],
                          "Required: description, doctor_id")

    def test_post_review_nodoctor(self):
        """
        Try to add a review for a non-existent doctor
        """
        header = {"Content-Type": "application/json"}
        data = json.dumps({"description": "A great doctor", "doctor_id": 999})
        response = self.app.post("/reviews", data=data, headers=header)
        rjson = json.loads(str(response.data, "utf-8"))
        self.assertTrue(response.status, 400)
        self.assertEquals(rjson["message"],
                          "Doctor does not exist with id: 999")

if __name__ == "__main__":
    unittest.main()