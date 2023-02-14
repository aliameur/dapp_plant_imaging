from flask import Blueprint
from .plant import plant_bp
from .imaging import imaging_bp

api_bp = Blueprint('api', __name__, url_prefix='/api')

api_bp.register_blueprint(plant_bp)
api_bp.register_blueprint(imaging_bp)


@api_bp.route('/config')
def config():
    import yaml
    # camera integration
    # total depth to use
    # total number of images
    # use yaml.dump to create it
    # use yaml to read and update and dump after update (apply button)
    pass

