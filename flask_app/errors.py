from flask import jsonify


def bad_request(msg):
    return msg, 400

def not_found(msg):
    return msg, 404

def not_authorized(msg):
    return msg, 401