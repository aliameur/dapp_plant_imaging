from flask import Blueprint, jsonify, request, abort
from .. import rabbitmq
import fireo
from ..models import Plant

imaging_bp = Blueprint('imaging', __name__, url_prefix='/imaging')


@imaging_bp.route('/sequence/<string:plant_id>')
def sequence(plant_id):
    plant = Plant.collection.get(plant_id)
    if not plant:
        return jsonify({"error": f"Plant {plant_id} does not exist."}), 404

    data = validate_json(request.get_json())
    if not data:
        return jsonify({"error": "Poorly formatted json body."})

    # send command to rpi, and get a response saying it started the sequence successfully
    # rpi does the sequence, and at the end it will upload to google storage
    message = f"start,{plant_id},{data}"
    response = rabbitmq.call("imaging", message)
    # TODO handle response
    return jsonify({"message": response})


def validate_json(json: dict):
    # TODO update validation function as we add parameters
    if "n_images" in json and isinstance(json["n_images"], int):
        return {"n_images": json["n_images"]}
    else:
        return None


@imaging_bp.errorhandler(415)
def unsupported_media_type(error):
    return jsonify({"error": "Did not attempt to load JSON data because the request Content-Type was not "
                             "'application/json'."}), 415
