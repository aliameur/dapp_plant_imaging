from flask import Blueprint, jsonify, request, current_app, abort
from .models import db, Plant, json_encoder, json_decoder, validate_json
import socket
from sqlalchemy.exc import SQLAlchemyError
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
    plant_id = request.args.get('plant_ids')
    plant = Plant.query.get(plant_id)
    plant_json = json_encoder(plant)
    return plant_json


@plant_bp.route('/get_current_conditions')
def get_current_conditions():
    # If plant_ids are passed in the request arguments, retrieve only those plants
    plant_ids = request.args.get('plant_ids')
    if plant_ids:
        plant_ids = plant_ids.split(',')
        plants = Plant.query.filter(Plant.id.in_(plant_ids)).all()
    else:
        # Otherwise, retrieve all plants
        plants = Plant.query.all()

    # If no plants are found, return a 404 response
    if not plants:
        return abort(404, "No plants found")

    # Serialize the plants and return them as a JSON response
    plants_json = [json_encoder(plant) for plant in plants]
    return jsonify(plants_json), 200


@plant_bp.route('/update_condition', methods=["PATCH"])
def update_condition():
    pass


@plant_bp.route('/update_conditions', methods=["PATCH"])
def update_conditions():
    pass


@plant_bp.route('/new_plant', methods=["POST"])
def new_plant():
    try:
        json = validate_json(request.json, (300, 800), (0, 35))
        plant = json_decoder(json)
        db.session.add(plant)
        db.session.commit()
        return jsonify({'message': f'Successfully added new plant'}), 200
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, 'An error occurred while adding the new plant')
    except ValueError as e:
        abort(500, e)


@plant_bp.route('/new_plants', methods=["POST"])
def new_plants():
    try:
        plant_json_list = [validate_json(i, (300, 800), (0, 35)) for i in request.json]
        plants = [json_decoder(plant_json) for plant_json in plant_json_list]
        db.session.add_all(plants)
        db.session.commit()
        return jsonify({'message': f'Successfully added {len(plants)} new plants'}), 200
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, 'An error occurred while adding the new plant')
    except ValueError as e:
        abort(500, e)
        # will only return first error found


@plant_bp.route('/set_plants', methods=["POST"])
def set_plants():
    pass


@plant_bp.route('/delete_plant/<int:plant_id>', methods=["DELETE"])
def delete_plant(plant_id):
    plant = Plant.query.get(plant_id)
    if not plant:
        abort(404, 'Plant not found')
    try:
        db.session.delete(plant)
        db.session.commit()
        return jsonify({'message': 'Plant deleted successfully'}), 200
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, 'An error occurred while deleting the plant')


@plant_bp.route('/delete_plants', methods=["DELETE"])
def delete_plants():
    plant_ids = request.args.get('plant_ids').split(",")

    if not plant_ids:
        abort(400, 'No plant ids provided')
    try:
        plants = Plant.query.filter(Plant.id.in_(plant_ids)).all()
        if len(plants) == 0:
            abort(404, 'No plants found')
        for plant in plants:
            db.session.delete(plant)
        db.session.commit()
        return jsonify({'message': f'Successfully deleted {len(plants)} plants'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(500, f'An error occurred while deleting plants {e}')


# Example usage: set LED brightness to 50%
# ip_address = '192.168.1.100'
# command = 'led'
# arg = 50
# send_command(ip_address, command, arg)
