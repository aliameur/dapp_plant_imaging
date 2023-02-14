from flask import Blueprint, jsonify, request
import socket
from dotenv import load_dotenv
import os

load_dotenv()
IP_ADDRESS = os.environ["IP_ADDRESS"]
plant_bp = Blueprint('plant', __name__, url_prefix='/plant')


@plant_bp.route('/')
def home():
    return jsonify({"message": "plant endpoint"})


@plant_bp.route('/conditions')
def conditions():
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
    sock.connect((IP_ADDRESS, 8888))
    if temperature != -1:
        sock.sendall(f'heat,{temperature},{plant_id}'.encode())
    if brightness != -1:
        sock.sendall(f'led,{brightness},{plant_id}'.encode())
    sock.close()

# Example usage: set LED brightness to 50%
# ip_address = '192.168.1.100'
# command = 'led'
# arg = 50
# send_command(ip_address, command, arg)
