from flask import Blueprint, jsonify, request, abort
from ... import rabbitmq

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


@imaging_bp.route('/sequence/<int:plant_id>')
def sequence(plant_id):
    # manual mode
    manual = request.args.get("manual", False, type=bool)

    # canon camera imaging
    # leave space for multiple camera integrations
    # save images per plant_id

    # send command to raspberry pi using RabbitMQ
    # e.g. send(direction, position)
