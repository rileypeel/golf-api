import json, unittest
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_app.models import Round, Tee, Course, User
from flask_app import create_app, db

def sample_user(db, name="Jon Snow"):
    user = User(name=name)
    db.session.add(user)
    db.session.commit()
    return user.id

def sample_course(db, name="Fake golf course", location="fake location"):
    course = Course(name=name, location=location)
    db.session.add(course)
    db.session.commit()
    return course.id

def sample_tee(db, course_id, colour="red"):
    tee = Tee(course_id=course_id, colour=colour)
    db.session.add(tee)
    db.session.commit()
    return tee.id

def sample_round(db, user_id, course_id, tee_id, full_detail=False):
    score_by_hole = [4, 4, 4, 4, 4, 4, 4, 4, 4]
    new_round = Round(
        course_id=course_id,
        tee_id=tee_id,
        user_id=user_id,
        score_by_hole=score_by_hole
    )

    if full_detail:
        putts = [2, 2, 2, 2, 2, 2, 2, 2, 2]
        #fairways = []
        #gir = []
    db.session.add(new_round)
    db.session.commit()
    return new_round.id

class UserTestCase(unittest.TestCase):
    """Class for testing User endpoints"""

    def setUp(self):
        """Set up for tests"""
        test_config = {
            'TEST_DB_URI': 'postgresql://test:password@db:5432/testdb'
        }
        self.app = create_app(test_config)
        self.client = self.app.test_client
        self.db = db
        self.db.create_all()

    def tearDown(self):
        """Test teardown"""
        self.db.session.remove()
        self.db.drop_all()

    #TODO test user authentication, for not just test the Round endpoints

    def test_retrieve_rounds(self):
        """Test retrieving rounds for associated user"""
        course1_id = sample_course(self.db)
        tee1_id = sample_tee(self.db, course1_id)
        user_id = sample_user(self.db)
        round1 = sample_round(self.db, user_id, course1_id, tee1_id)
        course2_id = sample_course(db, name="Another fake course")
        tee2_id = sample_tee(self.db, course2_id)
        round2 = sample_round(self.db, user_id, course2_id, tee2_id)
        res = self.client().get(f"users/{user_id}/rounds",)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data), 2)
        #TODO more assertions

    def test_post_partial_round_success(self):
        """Test posting a round with just score is successful"""
        course_id = sample_course(db)
        tee_id = sample_tee(self.db, course_id)
        user_id = sample_user(self.db)
        score = [4, 4, 4, 4, 4, 4, 4, 4, 4]
        payload = {
            "course_id": course_id,
            "tee_id": tee_id,
            'score_by_hole': score
        }
        res = self.client().post(
            f"users/{user_id}/rounds",
            data=json.dumps(payload)
        )
        self.assertEqual(res.status_code, 201)
        round = Round.query.filter_by(user_id=user_id).first()
        self.assertEqual(round.tee_id, payload['tee_id'])
        self.assertEqual(round.course_id, payload['course_id'])
        self.assertCountEqual(round.score_by_hole, score)

    def test_post_full_round_success(self):
        """Test posting a round with putts, fairways, GIR is successful"""
        course_id = sample_course(self.db)
        tee_id = sample_tee(self.db, course_id)
        user_id = sample_user(self.db)
        score = [4, 4, 4, 4, 4, 4, 4, 4, 4]
        putts = [2, 1, 2, 3, 4, 2, 1, 2, 2]
        fairways = [] #TODO
        gir = [] #TODO
        payload = {
            'course_id': course_id,
            'tee_id': tee_id,
            'score_by_hole': score,
            'putts': putts,
            'fairways': fairways,
            'gir': gir
        }
        res = self.client().post(
            f"users/{user_id}/rounds",
            data=json.dumps(payload)
        )
        self.assertEqual(res.status_code, 201)
        #TODO more assertions

    def test_post_round_fail(self):
        """Test posting a round with invalid course or tee_id's fails"""
        user_id = sample_user(self.db)
        course1_id = sample_course(self.db)
        course2_id = sample_course(self.db)
        tee2_id = sample_tee(self.db, course2_id)
        score = [4, 4, 4, 4, 4, 4, 4, 4, 4]
        payload = {
            'course_id': course1_id,
            'tee_id': tee2_id,
            'score_by_hole': score
        }
        res = self.client().post(
            f"users/{user_id}/rounds",
            data=json.dumps(payload)
        )

        self.assertEqual(res.status_code, 400)

    def test_retrieve_round_detail(self):
        """Test retrieving round detail"""
        course_id = sample_course(self.db)
        tee_id = sample_tee(self.db, course_id)
        user_id = sample_user(self.db)
        round_id = sample_round(self.db, user_id, course_id, tee_id)
        res = self.client().get(
            f"users/{user_id}/rounds/{round_id}",
        )
        self.assertEqual(res.status_code, 200)

    def test_update_round_success(self):
        """Test updating the round is successful"""
        course_id = sample_course(self.db)
        tee_id = sample_tee(self.db, course_id)
        user_id = sample_user(self.db)
        round_id = sample_round(self.db, user_id, course_id, tee_id)
        payload = {
            'score_by_hole': [5, 5, 5, 5, 5, 5, 5, 5, 5]
        }
        res = self.client().patch(
            f"users/{user_id}/rounds/{round_id}",
            data=json.dumps(payload)
        )
        round = Round.query.get(round_id)
        self.assertEqual(res.status_code, 201)
        self.assertCountEqual(round.score_by_hole, payload['score_by_hole'])

    def test_update_round_fail(self): #TODO might change functionality to let this happen
        """Test trying to change tee id or course id for a roumd fails"""
        course1_id = sample_course(self.db)
        tee1_id = sample_tee(self.db, course1_id)
        user_id = sample_user(self.db)
        round_id = sample_round(self.db, user_id, course1_id, tee1_id)
        course2_id = sample_course(self.db)
        tee2_id = sample_tee(self.db, course2_id)
        payload = {
            'course_id': course2_id,
            'tee_id': tee2_id
        } 
        res = self.client().patch(
            f"users/{user_id}/rounds/{round_id}",
            data=json.dumps(payload)
        )
        #self.assertEqual(res.status_code, 400)
        #self.assertEqual(round.course_id, course.id)
        #self.assertEqual(round.tee_id, tee.id)

if __name__ == "__main__":
    unittest.main()