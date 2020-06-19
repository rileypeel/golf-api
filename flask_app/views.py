from flask import Blueprint, jsonify, request, abort
from flask_app.models import Course
from flask_app import db

PAGE_SIZE = 10
course_bp = Blueprint('courses', __name__, url_prefix='/courses')
user_bp = Blueprint('user', __name__, url_defaults='/user')

@course_bp.route('', methods=["POST", "GET"])
def retrieve_courses():
    """Endpoint for courses, GET will return all courses in db by default,
    POST allows user to add a course to the database."""
    if request.method == 'POST':
        data = request.get_json(force=True)
        try:
            new_course = Course(**data)
            db.session.add(new_course)
            db.session.commit()
        except Exception as ex: #TODO tighten this up 
            abort(400, str(ex))

        #TODO change this so it returns the created course
        return jsonify({'message': 'success'}), 201

    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        start = (PAGE_SIZE * page - 1)
        end = start + PAGE_SIZE 
        courses = Course.query.all()
        formatted_courses = [course.format() for course in courses[start:end]]
        
        return jsonify(formatted_courses), 200

@course_bp.route('/<int:id>', methods=["GET"])
def course_detail(id):
    pass

@course_bp.route('/<int:id>/update', methods=["POST", "PATCH", "PUT"])
def course_update(id):
    pass

@user_bp.route('/<int:id>')
def user_detail(id):
    pass

@user_bp.route('<int:id>/update')
def user_update(id):
    pass

@user_bp.route('<int:id>/round')
def user_rounds(id):
    pass

@user_bp.route('<int:id>/round/<int:round_id>')
def round_detail(id, round_id):
    pass