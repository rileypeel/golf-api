from flask import Blueprint

course_bp = Blueprint('course', __name__, url_prefix='/course')
user_bp = Blueprint('user', __name__, url_defaults='/user')

@course_bp.route('', methods=["POST", "GET"])
def list_courses():
    pass

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