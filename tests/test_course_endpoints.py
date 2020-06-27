import json, unittest
from flask import jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_app import create_app, db
from flask_app.models import Course, Tee, Hole, Yardage


def sample_course(db, name="Fake golf course", tees=False):
    course = Course(name=name)
    db.session.add(course)
    if tees:
        tee1 = Tee(course=course, colour="red")
        tee2 = Tee(course=course, colour="blue")
        db.session.add(tee1)
        db.session.add(tee2)
    db.session.commit()
    return course

def sample_scorecard_payload(yardages=True):
    """Helper method returns a scorecard payload for a post request"""
    tee_yardages = []
    if yardages:
        tee_yardages = [{'colour': 'blue', 'yardage': 99}, {'colour': 'red', 'yardage': 101}]
    holes_list = [{'number': x, 'par': 4, 'tees': tee_yardages} for x in range(1, 10)]

    scorecard = {
        'tees': [
            {'colour': 'red'}, {'colour': 'blue'}
        ],
        'holes': holes_list,
    }
    return scorecard

class CourseTestCase(unittest.TestCase):
    """Class for testing Course endpoints"""

    def setUp(self):
        """Set up for tests"""
        test_config = {'TEST_DB_URI': 'postgresql://test:password@db:5432/testdb'}
        self.app = create_app(test_config)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.request_ctx = self.app.test_request_context()
        self.request_ctx.push()
        self.client = self.app.test_client
        self.db = db
        self.db.create_all()

    def tearDown(self):
        """Test teardown"""
        self.ctx.pop()
        self.request_ctx.pop()
        self.db.session.remove()
        self.db.drop_all()

    def test_post_course_success(self):
        """Test sending valid post request to /courses succeeds"""
        course_payload = {"name": "pretty fake golf course", "location": "fake location"}
        with self.app.app_context():
            res = self.client().post(
                url_for('courses.retrieve_courses'),
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
            url_for('courses.retrieve_courses'),
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
        course1 = Course(self.db, name="fake course", location="fake location")
        self.db.session.add(course1)
        self.db.session.commit()
        res = self.client().get(url_for("courses.retrieve_courses"))
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data), 1)

    def test_retrieve_holes(self):
        """Test retrieving holes, for a given course"""
        course = sample_course(self.db)
        hole1 = Hole(course=course, number=1, par=3)
        hole2 = Hole(course=course, number=2, par=4)
        self.db.session.add(hole1)
        self.db.session.add(hole2)
        self.db.session.commit()
        res = self.client().get(url_for("courses.retrieve_holes", id=course.id))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data), 2)

    def test_post_one_hole_success_no_yardage(self):
        """Test successful post request of one hole to /courses/<course id>/holes,
        without any associated yardage value"""
        course = sample_course(self.db)
        hole_payload = {'number': 1, 'par': 5}
        res = self.client().post(
            url_for("courses.retrieve_holes", id=course.id),
            data=json.dumps(hole_payload)
        )
        self.assertEqual(res.status_code, 201)
        #TODO test for location header
        hole = Hole.query.filter_by(course=course).first()
        self.assertIsNotNone(hole)
        self.assertEqual(hole.number, hole_payload['number'])
        self.assertEqual(hole.par, hole_payload['par'])

    def test_post_many_holes_success_no_yardage(self):
        """Test successful post request of many holes to /courses/<course id>/holes,
        without any associated yardage values"""
        course = sample_course(self.db)
        holes_payload = [{'number': 1, 'par': 5}, {'number': 2, 'par': 4}]
        res = self.client().post(
            url_for("courses.retrieve_holes", id=course.id),
            data=json.dumps(holes_payload)
        )
        self.assertEqual(res.status_code, 201)
        #TODO check header for location
        holes = Hole.query.filter_by(course=course).all()
        self.assertEqual(len(holes), 2)
        for hole in holes:
            self.assertIn(hole.format(), holes_payload)
    
    def test_post_one_hole_success_with_yardage(self):
        """Test successful post request of one hole to /courses/<course id>/holes,
        with yardage value"""
        course = sample_course(self.db, tees=True)
        tees = course.tees
        tee1 = {'colour': tees[0].colour, 'yardage': 150},
        tee2 = {'colour': tees[1].colour, 'yardage': 200}
        hole_payload = {
            'number': 1,
            'par': 5, 
            'tees': [
                tee1,
                tee2
            ]
        }
        res = self.client().post(
            url_for("courses.retrieve_holes", id=course.id),
            data=json.dumps(hole_payload)
        )
        self.assertEqual(res.status_code, 201)
        #TODO get header
        hole = Hole.query.filter_by(course=course).first()
        self.assertIsNotNone(hole)
        self.assertEqual(hole.number, hole_payload['number'])
        self.assertEqual(hole.par, hole_payload['par'])
        self.assertEqual(len(hole.tees), 2)
        self.assertCountEqual(
            (tee1['colour'], tee2['colour']),
            (hole.tees[0].colour, hole.tees[1].colour)
        )
        self.assertCountEqual(
            (tee1['yardage'], tee2['yardage']),
            (hole.tees[0].colour, hole.tees[1].colour)
        )



    def test_post_many_holes_success_with_yardage(self):
        """Test successful post request of many holes to /courses/<course id>/holes,
        with yardage values"""
        course = sample_course(self.db, tees=True)
        tees = course.tees
        tee1 = {'colour': tees[0].colour, 'yardage': 150}
        tee2 = {'colour': tees[1].colour, 'yardage': 200}
        tee3 = {'colour': tees[0].colour, 'yardage': 400}
        tee4 = {'colour': tees[1].colour, 'yardage': 500}
        hole1 = {'number': 1, 'par': 5, 'tees': [tee1, tee2]}
        hole2 = {'number': 2, 'par': 4, 'tees': [tee3, tee4]}
        holes_payload = {
            'holes': [hole1, hole2]
        }
        res = self.client().post(
            url_for("courses.retrieve_holes", id=course.id),
            data=json.dumps(holes_payload)
        )
        self.assertEqual(res.status_code, 201)
        #TODO get header
        holes = Hole.query.filter_by(course=course).all()
        self.assertEqual(len(holes), 2)
        #maybe do more assertions, but this will probably do

    def test_retrieve_hole_detail(self):
        """Test retrieval of hole detail"""
        course = sample_course(self.db)
        hole = Hole(course=course, number=1, par=5)
        self.db.session.add(hole)
        self.db.session.commit()
        res = self.client().get(
            url_for("courses.hole_detail",
            id=course.id,
            hole_id=hole.id)
        )
        self.assertEqual(res.status_code, 200)
        self.assertDictEqual(hole.detail_format(), json.loads(res.data))

    def test_update_hole_success(self):
        """Test successful partial update of a hole with a PATCH request"""
        course = sample_course(self.db, tees=True)

        hole = Hole(course=course, number=1, par=4)
        self.db.session.add(hole)
        yardage = Yardage(hole=hole, tee=course.tees[0], yardage=150)
        self.db.session.add(yardage)
        self.db.session.commit()
        new_yardage = 200
        patch_payload = {
            'tees': {'colour': course.tees[0].colour, 'yardage': new_yardage}
        }
        res = self.client().patch(
            url_for("courses.hole_detail",
            id=course.id,
            hole_id=hole.id),
            data=json.dumps(patch_payload)
        )
        self.assertEqual(res.status_code, 200) #TODO maybe change code..
        yardage = Yardage.query.get((hole.id, course.tees[0].id)) #TODO not sure if this will work
        self.assertEqual(yardage.yardage, new_yardage)

    def test_update_hole_fail(self):
        """Test PATCH to change the par of a hole or the number of the hole fails"""
        course = sample_course(self.db, tees=True)
        hole_number = 1
        hole_par = 4
        hole = Hole(course=course, number=hole_number, par=hole_par)
        self.db.session.add(hole)
        self.db.session.commit()
        patch_payload = {
            'number': 2
        }
        res = self.client().patch(
            url_for("courses.hole_detail",
            id=course.id,
            hole_id=hole.id),
            data=json.dumps(patch_payload)
        )
        self.assertEqual(res.status_code, 400) 
        self.assertEqual(hole.number, hole_number)
        patch_payload = {
            'par': 4
        }
        res = self.client().patch(
            url_for("courses.hole_detail",
            id=course.id,
            hole_id=hole.id),
            data=json.dumps(patch_payload)
        )
        self.assertEqual(res.status_code, 400) 
        self.assertEqual(hole.par, hole_par)


    def test_retrieve_course_tees(self):
        """Test retrieving the tees for a course"""
        course = sample_course(self.db, tees=True)
        res = self.client().get(url_for('courses.retrieve_tees'))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(course.tees), len(data))

    def test_post_new_tee(self):
        """Test POST request to add a tee to the course"""
        course = sample_course(self.db)
        payload = {
            'colour': 'blue'
        }
        res = self.client().post(
            url_for('courses.retrieve_tees'),
            data=json.dumps(payload)
        )
        self.assertEqual(res.status_code, 201)
        tee = Tee.query.filter_by(course=course).first()
        self.assertEqual(tee.colour, payload['colour'])

    def test_post_new_tee_fail(self):
        """Test posting a tee with a non unique colour fails"""
        course = sample_course(self.db)
        tee_colour = 'blue'
        tee = Tee(course=course, colour=tee_colour)
        self.db.session.add(tee)
        self.db.session.commit()
        payload = {
            'colour': 'blue'
        }
        res = self.client().post(
            url_for('courses.retrieve_tees'),
            data=json.dumps(payload)
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(len(course.tees), 1)

    def test_retrieve_tee_detail(self):
        """Test retrieving tee detail"""
        course = sample_course(self.db, tees=True)
        tee = course.tees[0]
        res = self.client().get(
            url_for("courses.tee_detail", id=course.id, tee_id=tee.id)
        )
        self.assertEqual(res.status_code, 200)
        #TODO more assertions

    def test_partial_update_tee_success(self):
        """Test updating tee with patch request is successful"""
        course = sample_course(self.db, tees=True)
        tee = course.tees[0]
        payload = {
            'course_rating': 72,
            'slope_rating': 120
        }
        res = self.client().patch(
            url_for("courses.tee_detail", id=course.id, tee_id=tee.id),
            data=json.dumps(payload)
        )
        self.assertEqual(res.status_code, 201) #TODO maybe different code
        #TODO more assertions

    def test_update_tee_fail(self):
        """Test update fails"""
        pass

if __name__ == "__main__":
    unittest.main()