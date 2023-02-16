from flask import Flask
from flask_bootstrap import Bootstrap5

from .api import create_module as api_create_module
from .dashboard import create_module as dashboard_create_module
from .main import create_module as main_create_module

bootstrap = Bootstrap5()


def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object,
                     e.g. project.config.ProdConfig
    """
    app = Flask(__name__)
    app.config.from_object(object_name)

    bootstrap.init_app(app)  # will be required for dashboard setup TODO add option to remove if only api used

    api_create_module(app)
    dashboard_create_module(app)
    main_create_module(app)

    return app
