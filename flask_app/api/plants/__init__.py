from .controllers import plants_bp
from flask_restful import Api
from .controllers import ConditionResource

api = Api(plants_bp)


def create_module(app, **kwargs):
    api.add_resource(ConditionResource,
                     '/',
                     '/<string:plant_id>')
    app.register_blueprint(plants_bp)
