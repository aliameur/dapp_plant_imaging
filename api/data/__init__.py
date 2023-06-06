from flask_restful import Api
from .controllers import PlantResource, HistoryResource, data_bp

api = Api(data_bp)


def create_module(app, **kwargs):
    api.add_resource(PlantResource, '/', '/<string:plant_id>')
    api.add_resource(HistoryResource, '/<string:plant_id>/history', '/<string:plant_id>/history/<string:history_id>')
    app.register_blueprint(data_bp)
