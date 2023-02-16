from .controllers import main_bp


def create_module(app, **kwargs):
    app.register_blueprint(main_bp)
