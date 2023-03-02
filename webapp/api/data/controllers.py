from flask import Blueprint, jsonify
from ..models import Plant

data_bp = Blueprint('data', __name__, url_prefix='/data')


@data_bp.route('/')
def home():
    response = {"message": "data endpoint"}
    return jsonify(response)
