from flask_app import db
from sqlalchemy.dialects import postgresql
from datetime import datetime

#TODO add user authentication later, for now just a name is fine

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    handicap = db.Column(db.Float, default=0)
    date_joined = db.Column(db.Date, default=datetime.date(datetime.now()))
    rounds = db.relationship('Round', backref='user', lazy=True)

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


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    #one to many with round
    #one to many with tee

class Tee(db.Model):
    __tablename__ = 'tees'
    id = db.Column(db.Integer, primary_key=True)
    colour = db.Column(db.String(), nullable=False)
    yardage = db.Column(db.Integer, nullable=True)
    rating = db.column(db.Float, nullable=True)
    #many to many with holes
    

class Hole(db.Model):
    __tablename__ = 'holes'
    id = db.Column(db.Integer, primary_key=True)
    #TODO check hole number is between 1 and 18
    number = db.Column(db.Integer, nullable=False)


#NEED a hole and tee association table with yardages
