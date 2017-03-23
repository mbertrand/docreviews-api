DOCREVIEWS API
=============
This API can be used to add, update, retrieve, and delete doctors and reviews.


Installation
------------
From the docreviews-api folder:

    pip install -r requirements.txt
    pip install -e .

Running the API
---------------

    python -m docreviews.api

By default the app will be running on port 5000


Customizing the database
------------------------

The default database is sqlite.  To use a different database, such as postgres:

- Make sure the database and database user already exist.

- Create a file that assigns SQLALCHEMY_DATABASE_URI to your database connection string, such as the following:
    - `SQLALCHEMY_DATABASE_URI = "postgresql://user:password@dbhost/docreviews"`

- Assign an environment variable to be equal to the above filename (including path), for example:
    - `export DOCREVIEWS_API_SETTINGS=/home/matt/custom_settings.cfg`

- start the application like this:
    `python -m docreviews.api --env_config DOCREVIEWS_API_SETTINGS`



Testing the API
---------------

    python -m unittest discover


API Endpoints
-------------

- /doctors
    - GET: Return all doctors in the database
    - POST: Add a doctor to the database (JSON data should include name)

- /doctors/<doctor_id>
    - GET: Return the doctor with the specified id
    - PATCH: Update the data for the doctor with the specified id
    - DELETE: Delete the doctor from the database

- /doctors/<doctor_id>/reviews/<review_id>
    - GET: Return the review of the doctor with the specified id's

- api/reviews
    - GET: Return all reviews in the database
    - POST: Add a review to the database (JSON data should include description, doctor_id)

- /reviews/<review_id>
    - GET: Return the review with the specified id
    - PATCH: Update the data for the review with the specified id
    - DELETE: Delete the review from the database
