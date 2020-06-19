import os, json, unittest
from flask_sqlalchemy import SQLAlchemy
from flask_app import create_app, db
from flask_app.models import User, Round

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
        new_user = User(name='Chris')
        self.db.session.add(new_user)
        self.db.session.commit()
        print(User.query.get(1))
        print("what the fuck")

        new_round = Round(user_id=1, score=score)
        self.db.session.add(new_round)
        self.db.session.commit()
        print(User.query.get(1))

        assert True


if __name__ == "__main__":
    unittest.main()