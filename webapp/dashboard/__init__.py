from .controllers import dashboard_bp


def create_module(app, **kwargs):
    app.register_blueprint(dashboard_bp)
