from flask import Blueprint, jsonify, request, abort, Response, url_for
from flask_app.models import Course, Hole, Yardage, Tee
from flask_app import db
from sqlalchemy.exc import DBAPIError
import traceback

PAGE_SIZE = 10
course_bp = Blueprint('courses', __name__, url_prefix='/courses')

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
            db.session.rollback() 
            abort(400, str(ex))
        return Response(
            headers={'Location': url_for('courses.course_detail', id=new_course.id)},
            status=201
        )

    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        start = PAGE_SIZE * (page - 1)
        end = start + PAGE_SIZE 
        courses = Course.query.all()
        formatted_courses = [course.format() for course in courses[start:end]]
        return jsonify(formatted_courses), 200

@course_bp.route('/<int:id>', methods=["GET", "PATCH"])
def course_detail(id):
    """Course detail endpoint, retrieve data for course with GET, update 
    course with PATCH"""
    if request.method == 'GET':
        course = Course.query.get(id)
        if course:
            return jsonify(course.detail_format()), 200
        abort(404, f"Course with id: {id} does not exist.")
    
    if request.method == 'PATCH':
        pass #TODO
        
@course_bp.route('/<int:id>/holes', methods=["GET", "POST"])
def retrieve_holes(id):
    """Retrieves holes for course with given id, you can also add holes
    for a course with a POST request, one at a time, or in bulk."""

    course = Course.query.get(id)
    if not course:
        return abort(404, f"Course with id: {id}, does not exist.")

    if request.method == 'GET':
        if not course.holes: 
            abort(
                404,
                "No holes for this course currently in the database"
            )
        formatted_holes = [hole.format() for hole in course.holes]
        return jsonify(formatted_holes), 200
        
    if request.method == 'POST':
        data = request.get_json(force=True)
        for hole_item in data:
            try:
                tees_list = []
                if 'tees' in hole_item.keys():
                    tees_list = hole_item.pop('tees')
                hole = Hole(course=course, **hole_item)
                db.session.add(hole)
                for tee_item in tees_list:
                    tee = Tee.query.filter_by(course=course, colour=tee_item['colour']).first()
                    yardage = Yardage(hole=hole, tee=tee, yardage=tee_item['yardage'])
                    db.session.add(yardage)
            except DBAPIError as ex:
                db.session.rollback()
                abort(400, f"""The following exception was 
                    raise while attempting to add holes to the database.
                    {str(ex)}""")
        try:
            db.session.commit()
        except DBAPIError as ex:
            db.session.rollback()
            abort(400, f"""The following exception was 
                raise while attempting to add holes to the database.
                {str(ex)}""")
        
        return Response(headers={'Location': url_for('courses.retrieve_holes', id=id)}, status=201)

@course_bp.route('/<int:id>/holes/<int:hole_id>', methods=["GET", "PATCH"])
def hole_detail(id, hole_id):
    """Endpoint for hole detail, update a hole record with a PATCH request, 
    retrieve course data with a GET request."""
    course = Course.query.get(id)
    if not course:
        abort(404, f"Cource with id: {id} was not found.")
    hole = Hole.query.get(hole_id)
    if not hole:
        abort(404, f"Hole with id: {hole_id} was not found.")
        
    if request.method == "GET":
        #TODO change primary key of hole 
        return jsonify(hole.detail_format()), 200
        
    if request.method == "PATCH":
        data = request.get_json(force=True)
        tee_items = data.pop('tees', None)
        if tee_items:
            for tee_item in tee_items: 
                tee = Tee.query.filter_by(
                    course=course,
                    colour=tee_item['colour']
                ).first() #TODO handle potential key error
                if not tee:
                    abort(400, "Bad request tee does not exist")
                yardage = Yardage.query.get((hole.id, tee.id))
                try:
                    if not yardage:
                        yardage = Yardage(tee=tee, hole=hole, yardage=0)
                    yardage.yardage = tee_item['yardage']
                    db.session.add(yardage)
                    db.session.commit()
                except DBAPIError as ex:
                    db.session.rollback()
                    abort(400, f"""The following exception occurred when attempting
                    to update the hole record in the database. {str(ex)}""")
                
        try:
            for key in data.keys():
                setattr(hole, key, data[key])
            db.session.commit()
        except DBAPIError as ex:
            db.session.rollback()
            abort(400, f"""The following exception occurred
                when attempting to update the hole object: {ex}""")
        return jsonify({}), 201 #TODO something better here 

@course_bp.route("/<int:id>/tees", methods=["GET", "POST"])
def retrieve_tees(id):
    """Endpoint for the tees of a course, retrieve all tees with a GET, 
    add a new tee to the course with a POST"""
    course = Course.query.get(id)
    if not course:
        abort(404, f"Course with id: {id}, does not exist.")

    if request.method == "POST":
        data = request.get_json(force=True)
        try:
            tee = Tee(course=course, **data)
            db.session.add(tee)
            db.session.commit()
            tee_id = tee.id
        except DBAPIError as ex:
            db.session.rollback()
            abort(400, f"""The following error occurred when attempting 
                to add the scorecard to the database. {str(ex)}""")
        return Response(
            headers={'Location': url_for('courses.tee_detail', id=course.id, tee_id=tee_id)},
            status=201
        )

    if request.method == "GET":
        print(f"course.tees {course.tees}")
        formatted_tees = [tee.format() for tee in course.tees]
        if not formatted_tees:
            abort(404, f"No tees exist for course with id: {id}.")
        return jsonify(formatted_tees), 200

@course_bp.route("<id>/tees/<tee_id>", methods=["GET", "PATCH"])
def tee_detail(id, tee_id):
    """Endpoint for tee detail, retrieve detailed tee data with a GET, 
    update tee detail with a PATCH"""
    course = Course.query.get(id)
    tee = Tee.query.get(tee_id)
    if not course or not tee:
        abort(404, "Tee does not exist") #TODO a little wonky change tee's primary key probably
    
    if request.method == "GET":
        return jsonify(tee.detail_format()), 200

    if request.method == "PATCH":
        data = request.get_json(force=True)
        if 'colour' in data.keys():
            abort(400, "Error, you cannot change a tee's colour.")
        try:
            for key in data.keys():
                setattr(tee, key, data[key])
            db.session.commit()
        except DBAPIError as ex:
            db.session.rollback()
            abort(400, f"""The following exception occurred
                when attempting to update the tee object: {ex}""")
        return jsonify({}), 201 #TODO something better here 