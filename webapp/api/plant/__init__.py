from .controllers import plant_bp


def create_module(app, **kwargs):
    app.register_blueprint(plant_bp)
