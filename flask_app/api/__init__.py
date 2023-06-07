from flask import Flask
from .rabbitmq import RabbitMQ
from firebase_admin import initialize_app

rabbitmq = RabbitMQ()


def create_app(object_name):
    """
    A flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object,
                     e.g. project.config.ProdConfig
    """
    app = Flask(__name__)
    app.config.from_object(object_name)

    rabbitmq.init_app(app)
    initialize_app()

    from .plants import create_module as plants_create_module
    from .imaging import create_module as imaging_create_module
    from .data import create_module as data_create_module
    from .auth import create_module as auth_create_module

    plants_create_module(app)
    imaging_create_module(app)
    data_create_module(app)
    auth_create_module(app)

    return app
