from flask import current_app
from flask_app import db
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import validates
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    date_joined = db.Column(db.Date, default=datetime.date(datetime.now()))
    rounds = db.relationship('Round', backref='user', lazy=True, order_by='Round.date') 

    @hybrid_property
    def handicap(self):
        """Calculate the user's handicap"""
        num_rounds = 0
        handicap_sum = 0
        for golf_round in self.rounds[:20]:
            pass
        return 30

    def __repr__(self):
        return f"<class User id: {self.id}, name: {self.name}," \
            f"handicap: {self.handicap}, date joined: {self.date_joined}"

    def format(self):
        """Return user object as a dict for JSON requests/responses"""
        user_dict = {
            'id': self.id,
            'name': self.name,
            'date_joined': self.date_joined
        }
        return user_dict

class Round(db.Model):
    __tablename__ = 'rounds'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    tee_id = db.Column(db.Integer, db.ForeignKey('tees.id'))
    date = db.Column(db.Date, default=datetime.date(datetime.now()))
    score_by_hole = db.Column(postgresql.ARRAY(db.Integer), nullable=False)
    putts = db.Column(postgresql.ARRAY(db.Integer), nullable=True)
    fairways = db.Column(postgresql.ARRAY(db.Integer), nullable=True)
    gir = db.Column(postgresql.ARRAY(db.Integer), nullable=True)

    @hybrid_property
    def handicap(self):
        """Property which returns calculated handicap differential value for the round"""
        rating, slope = self.tee.course_rating, self.tee.slope_rating #TODO watch out for None vals
        return (slope / 113) * score - rating

    @hybrid_property
    def score(self):
        """Compute total score."""
        cumulative_score = 0
        for s in self.score_by_hole:
            cumulative_score += s
        return cumulative_score

    @validates('tee_id')
    def validate_tee_id(self, key, tee_id):
        """Validate that the given tee is associated with the given course"""
        if self.tee not in self.course.tees:
            raise ValueError("Tee id and course id do not match.")
        return tee_id

    @validates('score')
    def validate_score(self, key, score):
        """Validate that score contains either 9 or 18 integer values"""
        if len(score) not in (9, 18):
            raise ValueError("Score should contain either 9 or 18 values")
        return score
        
    def __repr__(self):
        return f"<class Round id: {self.id}," \
            f" user id: {self.user_id}, course id: {self.course_id}, tee id: {self.tee_id}," \
            f" data: {self.date}, score: {self.score}>"

    def format(self):
        """Return round object basic data as a dictionary for JSON requests/responses"""
        round_dict = {
            'user_id': self.user_id,
            'course_id': self.course_id,
            'tee_id': self.tee_id,
            'handicap': self.handicap,
            'score': self.score
        }
        return round_dict

    def detail_format(self):
        """Return round object full data as a dictionary for JSON requests/responses"""
        round_dict = self.format()
        round_dict['score_by_hole'] = self.score_by_hole
        if self.putts: round_dict['putts'] = self.putts
        if self.fairways: round_dict['fairways'] = self.fairways
        if self.gir: round_dict['gir'] = self.gir
        return round_dict

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    location = db.Column(db.String(), nullable=False)
    rounds = db.relationship('Round', backref="course", lazy=True)
    holes = db.relationship('Hole', backref="course", lazy=True)
    tees = db.relationship('Tee', backref="course", lazy=True)

    @hybrid_property
    def par(self):
        course_par = 0
        for hole in self.holes:
            course_par += hole.par
        return course_par

    @hybrid_property
    def number_of_holes(self):
        return len(self.holes)

    def format(self):
        """Return basic info of the object as a dictionary"""
        return {'id': self.id, 'name': self.name}

    def detail_format(self):
        """Returned a more detailed format, including holes and tees."""
        #TODO for now just call for
        return self.format()


class Yardage(db.Model):
    __tablename__ = 'yardages'
    __table_args__ = (
        db.PrimaryKeyConstraint('tee_id', 'hole_id'),
    )
    tee_id = db.Column(db.Integer, db.ForeignKey('tees.id'), primary_key=True)
    hole_id = db.Column(db.Integer, db.ForeignKey('holes.id'), primary_key=True)
    yardage = db.Column(db.Integer, nullable=False)
    hole = db.relationship("Hole", back_populates="tees")
    tee = db.relationship("Tee", back_populates="holes")


class Tee(db.Model):
    __tablename__ = 'tees'
    __table_args__ = (
        db.UniqueConstraint('course_id', 'colour', name='course_colour_unique'),
    )
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    colour = db.Column(db.String(), nullable=False)
    course_rating = db.Column(db.Float, nullable=True)
    slope_rating = db.Column(db.Float, nullable=True)
    holes = db.relationship("Yardage", back_populates="tee")
    rounds = db.relationship("Round", backref="tee")

    @hybrid_property
    def yardage(self):
        """Calculate total yardage of the course"""
        total_yardage = 0
        for hole in self.holes:
            total_yardage += hole.yardage
        return total_yardage

    def format(self):
        tee_format = {
            'id': self.id,
            'course_id': self.course_id,
            'colour': self.colour
        }
        return tee_format

    def detail_format(self):
        tee_detail_format = self.format()
        tee_detail_format['course_rating'] = self.course_rating
        tee_detail_format['slope_rating'] = self.slope_rating
        return tee_detail_format


class Hole(db.Model):
    __tablename__ = 'holes'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    number = db.Column(db.Integer, nullable=False)
    par = db.Column(db.Integer, nullable=False)
    tees = db.relationship("Yardage", back_populates="hole")

    @validates('number')
    def validate_number(self, key, number):
        """Validate all hole numbers are between 1 and 18"""
        if number < 1 or number > 18:
            raise ValueError(f"hole number must be between 1 and 18")
        return number

    @validates('par')
    def validate_par(self, key, par):
        """Validate the par for a hole must be 3, 4, or 5"""
        if par not in (3, 4, 5):
            raise ValueError(f"par may only be 3, 4 or 5.")
        return par

    def format(self):
        """Return basic hole data as a dictionary for JSON requests/responses"""
        hole_dict = {
            'course_id': self.course_id,
            'number': self.number,
            'par': self.par,
        }
        return hole_dict

    def detail_format(self):
        """Return more detailed hole data as dictionary for JSON requests/responses"""
        hole_dict = self.format()
        hole_dict['tees'] = []
        for tee in self.tees:
            tee_dict = {}
            tee_dict['yardage'] = tee.yardage
            tee_dict['tee_id'] = tee.tee.id
            tee_dict['colour'] = tee.tee.colour
            hole_dict['tees'].append(tee_dict)
        return hole_dict
