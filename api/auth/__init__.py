from flask import request, jsonify
import firebase_admin
from .. import firebase


def create_module(app, **kwargs):
    @app.before_request
    def before_request():
        auth_header = request.headers.get('Authorization', None)

        if not auth_header:
            return jsonify({"error": "Missing authentication."}), 401

        try:
            token = auth_header.split(" ")[1]

            decoded_token = firebase.auth().verify_id_token(token)
            uid = decoded_token['uid']
        except firebase_admin.auth.InvalidIdTokenError:
            return jsonify({"error": "Token is invalid."}), 401
