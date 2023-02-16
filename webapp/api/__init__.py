from .controllers import api_bp


def create_module(app, **kwargs):
    app.register_blueprint(api_bp)
