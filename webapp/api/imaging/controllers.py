from flask import Blueprint, jsonify, request

imaging_bp = Blueprint('imaging', __name__, url_prefix='/imaging')


@imaging_bp.route('/start_imaging_sequence')
def start_imaging_sequence():
    # canon camera imaging
    # leave space for multiple camera integrations
    # manual mode
    plant_id = request.args["plant_id"]
    # save images per plant_id
    pass


@imaging_bp.route("/")
def home():
    return jsonify({"message": "imaging endpoint"})


# TODO swap plants
# TODO manual mode, position camera correctly
# TODO make cannon integration modular
#
