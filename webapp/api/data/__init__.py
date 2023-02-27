from .controllers import data_bp


def create_module(app, **kwargs):
    app.register_blueprint(data_bp)
