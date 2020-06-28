import json, unittest
from flask import jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_app import create_app, db
from flask_app.models import Course, Tee, Hole, Yardage

#TODO test retrieve course detail and test update course

def sample_tee(db, course_id, colour="red"):
    tee1 = Tee(course_id=course_id, colour=colour)
    db.session.add(tee1)
    db.session.commit()
    return tee1.id

def sample_course(db, name="Fake golf course", location="fake location"):
    course = Course(name=name, location=location)
    db.session.add(course)
    db.session.commit()
    return course.id


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
        course_payload = {
            "name": "pretty fake golf course",
            "location": "fake location"
        }
        res = self.client().post(
            "/courses",
            data=json.dumps(course_payload)
        )
        self.assertEqual(res.status_code, 201)
        course = Course.query.filter_by(name=course_payload["name"]).first()
        self.assertIsNotNone(course)
        self.assertEqual(course.location, course_payload['location'])

    def test_post_course_fail(self):
        """Test post request to /courses with no name or location returns 400"""
        invalid_course_payload = {'location': 'fake location'}
        res = self.client().post(
            "courses",
            data=json.dumps(invalid_course_payload)
        )
        self.assertEqual(res.status_code, 400)
        course = Course.query.filter_by(name=invalid_course_payload["location"]).first()
        self.assertIsNone(course)
        invalid_course_payload = {'name': 'Fake course'}
        res = self.client().post('/courses', data=json.dumps(invalid_course_payload))
        self.assertEqual(res.status_code, 400)
        course = Course.query.filter_by(name=invalid_course_payload["name"]).first()
        self.assertIsNone(course)

    def test_retrieve_courses_success(self):
        """Test retrieving courses with a get request"""
        course_id = sample_course(self.db, name="fake course", location="fake location")
        res = self.client().get("/courses")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 1)

    def test_retrieve_holes(self):
        """Test retrieving holes, for a given course"""
        course_id = sample_course(self.db)
        hole1 = Hole(course_id=course_id, number=1, par=3)
        hole2 = Hole(course_id=course_id, number=2, par=4)
        self.db.session.add(hole1)
        self.db.session.add(hole2)
        self.db.session.commit()
        res = self.client().get(f"/courses/{course_id}/holes")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data), 2)

    def test_post_one_hole_success_no_yardage(self):
        """Test successful post request of one hole to /courses/<course id>/holes,
        without any associated yardage value"""
        course_id = sample_course(self.db)
        hole_payload = [{'number': 1, 'par': 5}]
        res = self.client().post(
            f"/courses/{course_id}/holes",
            data=json.dumps(hole_payload)
        )
        self.assertEqual(res.status_code, 201)
        #TODO test for location header
        hole = Hole.query.filter_by(course_id=course_id).first()
        self.assertIsNotNone(hole)
        self.assertEqual(hole.number, hole_payload[0]['number'])
        self.assertEqual(hole.par, hole_payload[0]['par'])

    def test_post_many_holes_success_no_yardage(self):
        """Test successful post request of many holes to /courses/<course id>/holes,
        without any associated yardage values"""
        course_id = sample_course(self.db)
        holes_payload = [
            {'course_id': course_id, 'number': 1, 'par': 5},
            {'course_id': course_id, 'number': 2, 'par': 4}
        ]
        res = self.client().post(
            f"/courses/{course_id}/holes",
            data=json.dumps(holes_payload)
        )
        self.assertEqual(res.status_code, 201)
        #TODO check header for location
        holes = Hole.query.filter_by(course_id=course_id).all()
        self.assertEqual(len(holes), 2)
        for hole in holes:
            self.assertIn(hole.format(), holes_payload)
    
    def test_post_one_hole_success_with_yardage(self):
        """Test successful post request of one hole to /courses/<course id>/holes,
        with yardage value"""
        course_id = sample_course(self.db)
        colour1, colour2 = 'blue', 'red'
        sample_tee(self.db, course_id, colour1)
        sample_tee(self.db, course_id, colour2)
        tee1 = {'colour': colour1, 'yardage': 150}
        tee2 = {'colour': colour2, 'yardage': 200}
        hole_payload = [{
            'number': 1,
            'par': 5, 
            'tees': [tee1, tee2]
        }]
        res = self.client().post(
            f"/courses/{course_id}/holes",
            data=json.dumps(hole_payload)
        )
        self.assertEqual(res.status_code, 201)
        #TODO get header
        hole = Hole.query.filter_by(course_id=course_id).first()
        self.assertIsNotNone(hole)
        self.assertEqual(hole.number, hole_payload[0]['number'])
        self.assertEqual(hole.par, hole_payload[0]['par'])
        self.assertEqual(len(hole.tees), 2)
        self.assertCountEqual(
            (tee1['colour'], tee2['colour']),
            (hole.tees[0].tee.colour, hole.tees[1].tee.colour)
        )
        self.assertCountEqual(
            (tee1['yardage'], tee2['yardage']),
            (hole.tees[0].yardage, hole.tees[1].yardage)
        )

    def test_post_many_holes_success_with_yardage(self):
        """Test successful post request of many holes to /courses/<course id>/holes,
        with yardage values"""
        course_id = sample_course(self.db)
        colour1, colour2 = 'blue', 'red'
        sample_tee(self.db, course_id, colour1)
        sample_tee(self.db, course_id, colour2)
        tee1 = {'colour': colour1, 'yardage': 150}
        tee2 = {'colour': colour2, 'yardage': 200}
        tee3 = {'colour': colour1, 'yardage': 400}
        tee4 = {'colour': colour2, 'yardage': 500}
        hole1 = {'number': 1, 'par': 5, 'tees': [tee1, tee2]}
        hole2 = {'number': 2, 'par': 4, 'tees': [tee3, tee4]}
        holes_payload = [
            hole1, hole2
        ]
        res = self.client().post(
            f"/courses/{course_id}/holes",
            data=json.dumps(holes_payload)
        )
        self.assertEqual(res.status_code, 201)
        #TODO get header
        holes = Hole.query.filter_by(course_id=course_id).all()
        self.assertEqual(len(holes), 2)
        #maybe do more assertions, but this will probably do
        #self.assertDictEqual(hole)

    def test_retrieve_hole_detail(self):
        """Test retrieval of hole detail"""
        course_id = sample_course(self.db)
        colour1, colour2 = 'blue', 'red'
        sample_tee(self.db, course_id, colour1)
        sample_tee(self.db, course_id, colour2)
        hole = Hole(course_id=course_id, number=1, par=5)
        self.db.session.add(hole)
        self.db.session.commit()
        res = self.client().get(
            f"/courses/{course_id}/holes/{hole.id}"
        )
        hole = Hole.query.get(hole.id)
        self.assertEqual(res.status_code, 200)
        self.assertDictEqual(hole.detail_format(), json.loads(res.data))

    def test_update_hole_success(self):
        """Test successful partial update of a hole with a PATCH request"""
        course_id = sample_course(self.db)
        colour1, colour2 = 'blue', 'red'
        tee_id = sample_tee(self.db, course_id, colour1)
        hole = Hole(course_id=course_id, number=1, par=4)
        self.db.session.add(hole)
        yardage = Yardage(hole=hole, tee_id=tee_id, yardage=150)
        self.db.session.add(yardage)
        self.db.session.commit()
        hole_id = hole.id
        new_yardage = 200
        patch_payload = {
            'tees': [{'colour': colour1, 'yardage': new_yardage}]
        }
        res = self.client().patch(
            f"/courses/{course_id}/holes/{hole_id}",
            data=json.dumps(patch_payload)
        )
        self.assertEqual(res.status_code, 201) #TODO maybe change code..
        yardage = Yardage.query.get((hole_id, tee_id)) #TODO not sure if this will work
        self.assertEqual(yardage.yardage, new_yardage)

    def test_update_hole_fail(self): #TODO not sure if I want this functionality or not yet
        """Test PATCH to change the par of a hole or the number of the hole fails"""
        course_id = sample_course(self.db)
        hole_number = 1
        hole_par = 4
        hole = Hole(course_id=course_id, number=hole_number, par=hole_par)
        self.db.session.add(hole)
        hole_id = hole.id
        self.db.session.commit()
        patch_payload = {
            'number': 2
        }
        res = self.client().patch(
            f"/courses/{course_id}/holes/{hole.id}",
            data=json.dumps(patch_payload)
        )
        #self.assertEqual(res.status_code, 400) 
        #self.assertEqual(hole.number, hole_number)
        patch_payload = {
            'par': 4
        }
        res = self.client().patch(
            f"/courses/{course_id}/holes/{hole_id}",
            data=json.dumps(patch_payload)
        )
        #self.assertEqual(res.status_code, 400) 
        #self.assertEqual(hole.par, hole_par)

    def test_retrieve_course_tees(self):
        """Test retrieving the tees for a course"""
        course_id = sample_course(self.db)
        colour1, colour2 = 'blue', 'red'
        sample_tee(self.db, course_id, colour1)
        sample_tee(self.db, course_id, colour2)
        res = self.client().get(f"/courses/{course_id}/tees")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        course = Course.query.get(course_id)
        self.assertEqual(len(course.tees), len(data))

    def test_post_new_tee(self):
        """Test POST request to add a tee to the course"""
        course_id = sample_course(self.db)
        payload = {
            'colour': 'blue'
        }
        res = self.client().post(
            f"/courses/{course_id}/tees",
            data=json.dumps(payload)
        )
        self.assertEqual(res.status_code, 201)
        tee = Tee.query.filter_by(course_id=course_id).first()
        self.assertEqual(tee.colour, payload['colour'])

    def test_post_new_tee_fail(self):
        """Test posting a tee with a non unique colour fails"""
        course_id = sample_course(self.db)
        colour = 'blue'
        tee = Tee(course_id=course_id, colour=colour)
        self.db.session.add(tee)
        self.db.session.commit()
        payload = {
            'colour': colour
        }
        res = self.client().post(
            f"/courses/{course_id}/tees",
            data=json.dumps(payload)
        )
        course = Course.query.get(course_id)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(len(course.tees), 1)

    def test_retrieve_tee_detail(self):
        """Test retrieving tee detail"""
        course_id = sample_course(self.db)
        colour1 = 'red'
        tee_id = sample_tee(self.db, course_id, colour1)
        res = self.client().get(
            f"/courses/{course_id}/tees/{tee_id}"
        )
        self.assertEqual(res.status_code, 200)
        #TODO more assertions

    def test_partial_update_tee_success(self):
        """Test updating tee with patch request is successful"""
        course_id = sample_course(self.db)
        colour1 = 'red'
        tee_id = sample_tee(self.db, course_id, colour1)
        payload = {
            'course_rating': 72,
            'slope_rating': 120
        }
        res = self.client().patch(
            f"/courses/{course_id}/tees/{tee_id}",
            data=json.dumps(payload)
        )
        self.assertEqual(res.status_code, 201) #TODO maybe different code
        #TODO more assertions

    def test_update_tee_fail(self):
        """Test update fails"""
        pass

if __name__ == "__main__":
    unittest.main(verbosity=2)