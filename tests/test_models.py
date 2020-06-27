import os, json, unittest
from flask_sqlalchemy import SQLAlchemy
from flask_app import create_app, db
import flask_app.models as models

def sample_course(name="Fake course"):
    return models.Course(name=name)

def sample_tee(colour="black"):
    return models.Tee(colour=colour)

class ModelTestCase(unittest.TestCase):
    """Class for testing Models"""

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

    def test_user_model(self):
        """blah blah blah"""
        score = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        new_user = models.User(name='Chris')
        #self.db.session.add(new_user)
        #self.db.session.commit()
        

        #new_round = models.Round(user_id=1, score=score)
        #self.db.session.add(new_round)
        #self.db.session.commit()
        #print(User.query.get(1))

        assert True

    def test_round(self):
        user = models.User(name='Riley')
        print(user)
        course = models.Course(name="Fake course")
        self.db.session.add(user)
        self.db.session.add(course)
        self.db.session.commit()
        tee = models.Tee(colour='red')
        course.tees.append(tee)
        self.db.session.commit()

        new_round = models.Round(user=user, course=course, tee=tee, score_by_hole=[1, 2, 3, 4, 5, 6, 7, 8, 9])
        print(new_round)
        self.db.session.add(new_round)
        self.db.session.commit()
        print(models.Round.query.get(3))
        assert True

    def test_hole_format(self):
        """Test the Hole model's format method"""
        course = sample_course()
        number, par = (1, 4)
        hole = models.Hole(course=course, number=number, par=par)
        self.db.session.add(course)
        self.db.session.add(hole)
        self.db.session.commit()
        hole_format = hole.format()
        self.assertEqual(hole_format['course_id'], course.id)
        self.assertEqual(hole_format['number'], number)
        self.assertEqual(hole_format['par'], par)

    def test_hole_detail_format(self):
        """Test the Hole model's detail format method"""
        course = sample_course()
        tee1 = sample_tee('blue')
        tee2 = sample_tee('red')
        self.db.session.add(course)
        self.db.session.add(tee1)
        self.db.session.add(tee2)
        number, par = (1, 4)
        hole = models.Hole(course=course, number=number, par=par)
        yardage1 = models.Yardage(hole=hole, tee=tee1, yardage=500)
        yardage2 = models.Yardage(hole=hole, tee=tee2, yardage=400)
        self.db.session.commit()
        hole_format = hole.detail_format()
        self.assertEqual(hole_format['course_id'], course.id)
        self.assertEqual(hole_format['number'], number)
        self.assertEqual(hole_format['par'], par)
        self.assertEqual(2, len(hole_format['tees']))
        #TODO the rest of the assertions here 

    def test_hole_invalid_par(self):
        """Test adding a hole with an invalid par raises value error"""
        with self.assertRaises(ValueError):
            hole = models.Hole(number=1, par=6)

    def test_hole_invalid_number(self):
        """Test adding a hole with an invalid number raises value"""
        with self.assertRaises(ValueError):
            hole = models.Hole(number=19, par=4)

        
if __name__ == "__main__":
    unittest.main()