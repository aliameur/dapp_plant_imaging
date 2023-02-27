from flask import Blueprint, jsonify, request
from .plant import plant_bp
from .imaging import imaging_bp

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/config')
def config():
    # camera integration
    # total depth to use
    # total number of images
    # use yaml.dump to create it
    # use yaml to read and update and dump after update (apply button)
    pass


@api_bp.route('/')
def home():
    response = {"message": "main api endpoint"}
    return jsonify(response)
