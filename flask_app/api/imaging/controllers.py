from flask import Blueprint, jsonify, request, abort
from .. import rabbitmq
import fireo
from ..models import Plant

imaging_bp = Blueprint('imaging', __name__, url_prefix='/imaging')


@imaging_bp.route("/")
def home():
    return jsonify({"message": "imaging endpoint"})


# TODO swap plants
# TODO manual mode, position camera correctly
# TODO make cannon integration modular


@imaging_bp.route('/control')
def control():
    direction = request.args.get("direction")
    position = request.args.get("position")
    if not direction:
        abort(400, "No direction provided.")
    if not position:
        abort(400, "No position provided.")
    if direction not in ("r", "z", "theta"):
        abort(404, "Direction does not exist, please use 'r', 'z', or 'theta'.")

    # send command to raspberry pi using RabbitMQ
    # e.g. send(direction, position)
    rabbitmq.call()


@imaging_bp.route('/sequence/<string:plant_id>')
def sequence(plant_id=None):
    # check that the plant exists on the fireo database
    if not plant_id:
        print(plant_id)


    plant = Plant.collection.get(plant_id)
    # check the json body
    #
    request.get_json()
    # manual mode
    manual = request.args.get("manual", False, type=bool)

    # canon camera imaging
    # leave space for multiple camera integrations
    # save images per plant_id

    # send command to raspberry pi using RabbitMQ
    # e.g. send(direction, position)


@imaging_bp.errorhandler(415)
def unsupported_media_type(error):
    return jsonify({"error": "Did not attempt to load JSON data because the request Content-Type was not 'application/json'."}), 415
