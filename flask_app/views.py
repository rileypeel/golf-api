from flask import Blueprint, jsonify, request, abort, Response, url_for
from flask_app.models import Course, Hole, Yardage, Tee
from flask_app import db
from sqlalchemy.exc import DBAPIError
import traceback

PAGE_SIZE = 10
course_bp = Blueprint('courses', __name__, url_prefix='/courses')
user_bp = Blueprint('users', __name__, url_defaults='/user')

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
        except DBAPIError as ex: 
            abort(400, str(ex))
        return Response(headers={'Location': url_for('courses.course_detail', id=new_course.id)}, status=201)

    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        start = PAGE_SIZE * (page - 1)
        end = start + PAGE_SIZE 
        courses = Course.query.all()
        formatted_courses = [course.format() for course in courses[start:end]]
        return jsonify(formatted_courses), 200

@course_bp.route('/<int:id>', methods=["GET", "PATCH"])
def course_detail(id):
    """Endpoint for getting data for course with the given id."""
    if request.method == 'GET':
        course = Course.query.get(id)
        if course:
            return jsonify(course.detail_format()), 200
        abort(404, f"Course with id: {id} does not exist.")
    
    if request.method == 'PATCH':
        pass #TODO


@course_bp.route('/<int:id>/scorecard', methods=["GET", "POST"])
def retrieve_scorecard(id):
    """Retrieves scorecard for course with given id, you can also POST a scorecard
    for a course if it does not already exist."""
    course = Course.query.get(id)
    if not course:
        return abort(404, f"Course with id: {id}, does not exist.")

    if request.method == 'GET':
        formatted_holes = [hole.detail_format() for hole in course.holes]
        formatted_tees = [tee.format() for tee in course.tees]
        return jsonify({'holes': formatted_holes, 'tees': formatted_tees}), 200
        
    if request.method == 'POST':
        if course.tees or course.holes:
            abort(400, "Scorecard for this course already exists.")

        data = request.get_json(force=True)
        holes_list = data.get('holes', None)
        tees_list = data.get('tees', None)
        if tees_list and holes_list:
            if len(holes_list) not in (9, 18): #TODO maybe do this in models instead
                abort(400, "Error: Please provide either 9 or 18 holes.")
            for i in range(1, len(holes_list)+1):
                if i not in [hole['number'] for hole in holes_list]: 
                    abort(400, "Error: Invalid hole numbers provided")

            for tee_item in tees_list:
                tees_by_colour = {}
                try:
                    tee = Tee(course=course, **tee_item)
                    db.session.add(tee)
                    tees_by_colour[tee_item['colour']] = tee
                    
                except DBAPIError as ex:
                    abort(400, f"""The following error occurred when attempting 
                        to add the scorecard to the database. {str(ex)}""")
            #print(tees_by_colour)
            for hole_item in holes_list:
                try:
                    tees_list = hole_item.pop('tees')
                    hole = Hole(course=course, **hole_item)
                    for tee_item in tees_list:
                        tee = tees_by_colour[tee_item['colour']]
                        yardage = Yardage(hole=hole, tee=tee, yardage=tee_item['yardage'])
                        db.session.add(yardage)
                    db.session.add(hole)
                    db.session.commit()
                except DBAPIError as ex:
                    abort(400, f"""The following exception was 
                        raise while attempting to add scorecard to the database.
                            {str(ex)}""")

            return Response(headers={'Location': url_for('courses.retrieve_scorecard', id=id)}, status=201)

        abort(400, "Error: not enough data provided.") 



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