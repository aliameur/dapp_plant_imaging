from .controllers import imaging_bp


def create_module(app, **kwargs):
    app.register_blueprint(imaging_bp)
