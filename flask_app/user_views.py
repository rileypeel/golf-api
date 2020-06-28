from flask import Blueprint, jsonify, request, abort, Response, url_for
from flask_app.models import Course, Hole, Yardage, Tee, User, Round
from flask_app import db
from sqlalchemy.exc import DBAPIError
import traceback

PAGE_SIZE = 10
user_bp = Blueprint('users', __name__, url_prefix='/users')

@user_bp.route('/<int:id>')
def user_detail(id):
    pass

@user_bp.route('/<int:id>/rounds', methods=["GET", "POST"])
def retrieve_rounds(id):
    """Endpoint for rounds associated with the user which has id, GET request
    will return user rounds, POST request to add a round for the user."""
    user = User.query.get(id)
    if not user:
        abort(404, f"User with id: {id} does not exist.")

    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        start = PAGE_SIZE * (page - 1)
        end = start + PAGE_SIZE 
        formatted_rounds = [round.format() for round in user.rounds[start:end]]
        if not formatted_rounds:
            abort(404, f"No rounds exist for user with id: {id}.")
        return jsonify(formatted_rounds), 200

    if request.method == 'POST':
        data = request.get_json(force=True)
        course = Course.query.get(data.pop('course_id', None))
        tee = Tee.query.get(data.pop('tee_id', None))
        if course and tee:
            try:
                new_round = Round(user=user, course=course, tee=tee, **data)
                db.session.add(new_round)
                db.session.commit()
            except DBAPIError as ex: 
                db.session.rollback()
                abort(400, f"Error adding round to database. {str(ex)}")
            except ValueError as ex:
                db.session.rollback()
                abort(400, f"The following value error occurred: {str(ex)}")
            return Response(
                headers={'Location': url_for(
                    'users.round_detail',
                    id=user.id,
                    round_id=new_round.id
                )},
                status=201
            )   
        abort(400, "Invalid course data provided.") 

@user_bp.route('/<int:id>/rounds/<int:round_id>', methods=["GET", "PATCH"])
def round_detail(id, round_id):
    """Round detail endpoint, GET request will return detailed data for 
    round record with round_id, PATCH request allows update of round record with
    round_id"""
    user = User.query.get(id)
    if not user:
        abort(404, f"User with id: {id} does not exist.")
    round = Round.query.get(round_id)
    if not round:
        abort(404, f"Round recorde with id: {round_id} does not exist.")

    if request.method == "GET": #TODO wonky like the other one
        return jsonify(round.detail_format()), 200

    if request.method == "PATCH":
        data = request.get_json(force=True)
        try:
            for key in data.keys():
                setattr(round, key, data[key])
            db.session.commit()
        except DBAPIError as ex:
            db.session.rollback()
            abort(400, f"""The following exception occurred when attempting
                to update the round: {str(ex)}""")

        return jsonify({}), 201