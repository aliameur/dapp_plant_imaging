from .controllers import plants_bp


def create_module(app, **kwargs):
    app.register_blueprint(plants_bp)
