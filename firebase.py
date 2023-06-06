import firebase_admin.auth
from flask import current_app
from firebase_admin import credentials, firestore, auth, initialize_app
import fireo


class Firebase:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    @staticmethod
    def init_app(app):
        cred = credentials.Certificate('firebase-config.json')
        firebase_app = initialize_app(cred)
        app.config['FIRESTORE'] = firestore.client(app=firebase_app)
        app.config['AUTH'] = auth._get_client(app=firebase_app)

    @staticmethod
    def firestore():
        return current_app.config['FIRESTORE']

    @staticmethod
    def auth() -> firebase_admin.auth.Client:
        return current_app.config['AUTH']
