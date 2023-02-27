from .controllers import api_bp
from .plant import create_module as plant_create_module
from .imaging import create_module as imaging_create_module
from .data import create_module as data_create_module


def create_module(app, **kwargs):
    plant_create_module(api_bp)
    imaging_create_module(api_bp)
    data_create_module(api_bp)

    app.register_blueprint(api_bp)
