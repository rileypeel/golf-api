from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_app.errors import bad_request, not_found, not_authorized
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    """Initialize flask application"""
    app = Flask(__name__)
    if test_config: #TODO clean this up 
        app.config["SQLALCHEMY_DATABASE_URI"] = test_config["TEST_DB_URI"]
        app.config["TESTING"] = True
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    app.register_error_handler(404, not_found)
    app.register_error_handler(400, bad_request)
    app.register_error_handler(401, not_authorized)

    from flask_app.course_views import course_bp
    app.register_blueprint(course_bp)
    from flask_app.user_views import user_bp
    app.register_blueprint(user_bp)

    return app


    