from flask import Blueprint, jsonify, request, abort, Response, url_for
from flask_app.models import Course, Hole, Yardage, Tee
from flask_app import db
from sqlalchemy.exc import DBAPIError
import traceback

PAGE_SIZE = 10
user_bp = Blueprint('users', __name__, url_defaults='/user')

@user_bp.route('/<int:id>')
def user_detail(id):
    pass

@user_bp.route('<int:id>/rounds', methods=["GET"])
def rounds(id):
    """Retrieve user rounds and/or post a new round"""

    if request.method == 'GET':
        pass

    if request.method == 'POST':
        data = request.get_json(force=True)
        course = Course.query.get(data.get('course_id', None))
        tee = Tee.query.get(data.get('tee_id', None))
        user = User.query.get(id)
        round_data = data.get('round', None)
        if course and tee and user:
            try:
                new_round = Round(user=user, course=course, tee=tee, **round_data)
                db.session.add(new_round)
                db.commit()
            except DBAPIError as ex: 
                abort(400, f"Error adding round to database. {ex}")
        abort(400, "Invalid data provided.") 

@user_bp.route('<int:id>/round/<int:round_id>', methods=["GET", "PATCH"])
def round_detail(id, round_id):
    pass