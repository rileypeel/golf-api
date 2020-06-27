import json, unittest
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_app import create_app, db

def sample_user(db, name="Jon Snow"):
    user = User(name=name)
    db.session.add(user)
    db.session.commit()
    return user

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

def sample_round(db, user, coures, tee, full_detail=False):
    score = [4, 4, 4, 4, 4, 4, 4, 4, 4]
    new_round = Round(course=course, tee=tee, user=user, score=score)

    if full_detail:
        putts = [2, 2, 2, 2, 2, 2, 2, 2, 2]
        #fairways = []
        #gir = []
    db.session.add(new_round)
    db.session.commit()
    return new_round

class UserTestCase(unittest.TestCase):
    """Class for testing User endpoints"""

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

    #TODO test user authentication, for not just test the Round endpoints

    def test_retrieve_rounds(self):
        """Test retrieving rounds for associated user"""
        course1 = sample_course(db, tees=True)
        tee1 = course.tees[0]
        user = sample_user()
        round1 = sample_round(self.db, user, course1, tee1)
        course2 = sample_course(db, name="Another fake course", tees=True)
        tee2 = course2.tees[0]
        round2 = sample_round(self.db, user, course2, tee2)
        res = self.client().get(url_for('users.retrieve_rounds', id=user.id))
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(len(data), 2)
        #TODO more assertions


    def test_post_partial_round_success(self):
        """Test posting a round with just score is successful"""
        course = sample_course(db, tees=True)
        tee = course.tees[0]
        user = sample_user()
        score = [4, 4, 4, 4, 4, 4, 4, 4, 4]
        payload = {
            "course_id": course.id,
            "tee_id": tee.id,
            'score': score
        }
        res = self.client().post(
            url_for('users.retrieve_rounds', id=user.id),
            data=json.dumps(payload)
        )
        self.assertEqual(res.status_code, 201)
        round = Round.query.filter_by(user=user).first()
        self.assertEqual(round.tee_id, payload['tee_id'])
        self.assertEqual(round.course_id, payload['course_id'])
        self.assertCountEqual(round.score, score)

    def test_post_full_round_success(self):
        """Test posting a round with putts, fairways, GIR is successful"""
        course = sample_course(db, tees=True)
        tee = course.tees[0]
        user = sample_user()
        score = [4, 4, 4, 4, 4, 4, 4, 4, 4]
        putts = [2, 1, 2, 3, 4, 2, 1, 2, 2]
        fairways = [] #TODO
        gir = [] #TODO
        payload = {
            'course_id': course1.id,
            'tee_id': tee2.id,
            'score': score,
            'putts': putts,
            'fairways': fairways,
            'gir': gir
        }
        res = self.client().post(
            url_for('user.retrieve_rounds', id=user.id),
            data=json.dumps(payload)
        )
        self.assertEqual(res.status_code, 201)
        #TODO more assertions

    def test_post_round_fail(self):
        """Test posting a round with invalid course or tee_id's fails"""
        user = sample_user()
        course1 = sample_course(db, tees=True)
        course2 = sample_course(db, tees=True)
        tee2 = course2.tees[0]
        score = [4, 4, 4, 4, 4, 4, 4, 4, 4]
        payload = {
            'course_id': course1.id,
            'tee_id': tee2.id,
            'score': score
        }
        res = self.client().post(
            url_for('user.retrieve_rounds', id=user.id),
            data=json.dumps(payload)
        )

        self.assertEqual(res.status_code, 400)

    def test_retrieve_round_detail(self):
        """Test retrieving round detail"""
        course = sample_course(db, tees=True)
        tee = course.tees[0]
        user = sample_user()
        round = sample_round(self.db, user, course, tee)
        res = self.client().get(
            url_for('users.round_detail', id=user.id, round_id=round.id)
        )
        self.assertEqual(res.status_code, 200)

    def test_update_round_success(self):
        """Test updating the round is successful"""
        course = sample_course(db, tees=True)
        tee = course.tees[0]
        user = sample_user()
        round = sample_round(self.db, user, course, tee)
        payload = {
            'score': [5, 5, 5, 5, 5, 5, 5, 5, 5]
        }
        self.client().patch(
            url_for("user.round_detail", id=user.id, round_id=round.id),
            data=json.dumps(payload)
        )
        self.assertEqual(res.status_code, 201)
        self.assertCountEqual(round.score, payload['score'])

    def test_update_round_fail(self):
        """Test trying to change tee id or course id for a roumd fails"""
        course = sample_course(db, tees=True)
        course2 = sample_course(db, tees=True)
        tee = course.tees[0]
        user = sample_user()
        round = sample_round(self.db, user, course, tee)
        payload = {
            'course_id': course2.id,
            'tee_id': course2.tees[0].id
        } 
        res = self.client().patch(
            url_for('user.round_detail', id=user.id, round_id=round.id),
            data=json.dumps(payload)
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(round.course_id, course.id)
        self.assertEqual(round.tee_id, tee.id)

if __name__ == "__main__":
    unittest.main()