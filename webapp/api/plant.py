from flask import Blueprint, jsonify, request, current_app
from .models import db, Plant, json_encoder
import socket

plant_bp = Blueprint('plant', __name__, url_prefix='/plant')


@plant_bp.route('/')
def home():
    return jsonify({"message": "plant endpoint"})


@plant_bp.route('/conditions')
def conditions():
    ip_address = current_app.config.PLANT_IP_ADDRESS
    # get argument values and check for errors
    plant_id = request.args.get("plant_id", default=-1)
    if plant_id == -1:
        return jsonify({"error": "please specify a plant_id"})
    temperature = request.args.get("temperature", default=-1, type=float)
    brightness = request.args.get("brightness", default=-1, type=int)
    if temperature == -1 and brightness == -1:
        return jsonify({"error": "please specify a condition"})

    # check for value bounds
    # TODO to update value bounds, ask em
    # TODO add value bounds on webapp w/ javascript
    if not 0 <= brightness <= 100 and brightness != -1:
        error_dict = {"error": ["brightness should be between 0 and 100"]}

    if not 0 <= temperature <= 50 and temperature != -1:
        try:
            error_dict["error"].append("temperature should be between 0 and 50")
        except NameError:
            error_dict = {"error": "temperature should be between 0 and 50"}
    try:
        return jsonify(error_dict)
    except NameError:
        pass

    # TODO test with raspberry pi ASAP
    # send command to raspberry pi over WIFI
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip_address, 8888))
    if temperature != -1:
        sock.sendall(f'heat,{temperature},{plant_id}'.encode())
    if brightness != -1:
        sock.sendall(f'led,{brightness},{plant_id}'.encode())
    sock.close()


@plant_bp.route('/get_current_condition')
def get_current_condition():
    # talk to rpi and get current conditions
    # TODO storage of information updated onto database, sql or mongodb?
    pass


@plant_bp.route('/get_current_conditions')
def get_current_conditions():
    # query all current plant conditions
    plants = Plant.query.all()
    plants_json = [json_encoder(plant) for plant in plants]
    return jsonify(plants_json)


@plant_bp.route('/update_condition', methods=["PATCH"])
def update_condition():
    pass


@plant_bp.route('/update_conditions', methods=["PATCH"])
def update_conditions():
    pass


@plant_bp.route('/new_plant', methods=["POST"])
def new_plant():
    pass


@plant_bp.route('/new_plants', methods=["POST"])
def new_plants():
    pass


@plant_bp.route('/set_plants', methods=["POST"])
def set_plants():
    pass


@plant_bp.route('/delete_plant', methods=["DELETE"])
def delete_plant():
    pass


@plant_bp.route('/delete_plants', methods=["DELETE"])
def delete_plants():
    pass

# Example usage: set LED brightness to 50%
# ip_address = '192.168.1.100'
# command = 'led'
# arg = 50
# send_command(ip_address, command, arg)