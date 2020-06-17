from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app(test_config=None):
    """Initialize flask application"""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    @app.after_request()
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorizatino')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    return app


    