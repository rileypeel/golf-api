import os, json, unittest
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_app import create_app, db
from flask_app.models import Course

class CourseTestCase(unittest.TestCase):
    """Class for testing Course endpoints"""

    def setUp(self):
        """Set up for tests"""
        test_config = {'TEST_DB_URI': 'postgresql://test:password@db:5432/testdb'}
        self.app = create_app(test_config)
        self.client = self.app.test_client
        self.db = db
        self.db.create_all()

    def tearDown(self):
        """Test teardown"""
        self.db.session.remove()
        self.db.drop_all()

    def test_post_course_success(self):
        """Test sending valid post request to /courses succeeds"""
        course_payload = {"name": "pretty fake golf course"}
        res = self.client().post('/courses', data=json.dumps(course_payload))
        self.assertEqual(res.status_code, 201)
        course = Course.query.filter_by(name=course_payload["name"]).first()
        self.assertTrue(course is not None)

    def test_post_course_fail(self):
        pass

    def test_retrieve_courses_success(self):
        """Test retrieving courses with a get request"""
        course1 = Course(name="fake course")
        self.db.session.add(course1)
        self.db.session.commit()
        res = self.client().get('/courses')
        data = json.loads(res.data)
        print(data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_retrieve_courses_fail(self):
        pass


if __name__ == "__main__":
    unittest.main()