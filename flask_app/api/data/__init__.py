from flask_restful import Api
from .controllers import PlantResource, HistoryResource, ImagesResource, data_bp

api = Api(data_bp)


def create_module(app, **kwargs):
    api.add_resource(PlantResource, '/', '/<string:plant_id>')
    api.add_resource(HistoryResource, '/<string:plant_id>/history', '/<string:plant_id>/history/<string:history_id>')
    api.add_resource(ImagesResource, '/<string:plant_id>/images', '/<string:plant_id>/images/<string:image_id>')
    app.register_blueprint(data_bp)
