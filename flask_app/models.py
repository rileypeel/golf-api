from flask import current_app
from flask_app import db
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from datetime import datetime

#TODO add user authentication later, for now just a name is fine
#add constraints and fix relationships then start with the endpoints


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    handicap = db.Column(db.Float, server_default="3", default=3, nullable=False)
    date_joined = db.Column(db.Date, default=datetime.date(datetime.now()))
    rounds = db.relationship('Round', backref='user', lazy=True)

    @hybrid_property
    def handicap(self):
        num_rounds = 0
        handicap_sum = 0
        # TODO put real handicap calculation in here
        for golf_round in self.rounds[:20]:
            num_rounds += 1
        return 69

    def __repr__(self):
        round_str = ""
        for golf_round in self.rounds:
            round_str += golf_round.__repr__()

        return f"asssname: {self.name}, handicap: {self.handicap}, date joined: {self.date_joined}, rounds: {round_str}"


class Round(db.Model):
    __tablename__ = 'rounds'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    tee_id = db.Column(db.Integer, db.ForeignKey('tees.id'))
    score = db.Column(postgresql.ARRAY(db.Integer), nullable=False)
    putts = db.Column(postgresql.ARRAY(db.Integer), nullable=True)
    fairways = db.Column(postgresql.ARRAY(db.Integer), nullable=True)
    gir = db.Column(postgresql.ARRAY(db.Integer), nullable=True)
    #TODO constraint to check that course id of tee foreign key is same as course id 

    @validates('tee_id')
    def validate_tee_id(self, key, tee_id):
        print(f"tee_id: {tee_id}")
        print(f"course_id: {self.course_id}")
        try: 
            Course.query.get(self.course_id).tees
        except:
            pass
        return tee_id

    @validates('score')
    def validate_score(self, key, score):
        if not (len(score) == 9 or len(score) == 18):
            raise ValueError("Score should contain either 9 or 18 values")

        if any(not isinstance(s, int) for s in score):
            raise TypeError("Score values must be of type int")
        print(f"key: {key}, score: {score}")
        return score
        
    def __repr__(self):
        return f"score: {self.score}"

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    #TODO location
    rounds = db.relationship('Round', backref="course", lazy=True)
    holes = db.relationship('Hole', backref="course", lazy=True)
    tees = db.relationship('Tee', backref="course", lazy=True)

yardages = db.Table('yardages',
    db.Column('yardage', db.Integer, nullable=False),
    db.Column('tee_id', db.Integer, db.ForeignKey('tees.id'), primary_key=True),
    db.Column('hole_id', db.Integer, db.ForeignKey('holes.id'), primary_key=True)
)

class Tee(db.Model):
    __tablename__ = 'tees'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    colour = db.Column(db.String(), nullable=False)
    tee_yardage = db.Column(db.Integer, nullable=True)
    course_rating = db.Column(db.Float, nullable=True)
    slope_rating = db.Column(db.Float, nullable=True)
    holes = db.relationship(
        'Hole',
        secondary=yardages,
        backref=db.backref('tees', lazy=True)
    )


class Hole(db.Model):
    __tablename__ = 'holes'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    number = db.Column(db.Integer, nullable=False)
    par = db.Column(db.Integer, nullable=False)

    @validates('number')
    def validate_number(self, key, number):
        if not isinstance(number, int):
            return TypeError("hole number must be of type integer.")
        if number < 1 or number > 18:
            return ValueError(f"hole number must be between 1 and 18")
        return number

    def __repr__(self):
        pass

    def __str__(self):
        pass

    def format(self):
        pass
