from flask import request, jsonify
from firebase_admin import auth


def create_module(app, **kwargs):
    @app.before_request
    def before_request():
        # if request.method != 'OPTIONS':
        #     auth_header = request.headers.get('Authorization', None)
        #
        #     if not auth_header:
        #         return jsonify({"error": "Missing authentication."}), 401
        #
        #     try:
        #         token = auth_header.split(" ")[1]
        #         decoded_token = auth.verify_id_token(token)
        #         uid = decoded_token['uid']
        #     except auth.InvalidIdTokenError:
        #         return jsonify({"error": "Token is invalid."}), 401
        pass