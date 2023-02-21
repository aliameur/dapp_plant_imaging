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


@plant_bp.route('/get_plant')
def get_plant():
    """
    Get the latest available conditions for a single plant (temperature, wavelength, brightness, name, and pin numbers),
    queried by plant id.

    Usage: plant_id is given as a URL request parameter. Returns the plant conditions as JSON.

    GET
    """
    plant_id = request.args.get('plant_id')  # get plant id from request parameter
    if not plant_id:
        abort(400, "No plant_id provided")
    plant = Plant.query.get(plant_id)  # query database
    if not plant:
        abort(404, "Plant not found")
    plant_json = json_encoder(plant)  # return result as json
    return plant_json


@plant_bp.route('/get_plants')
def get_plants():
    """
    Get the latest available conditions for multiple plants (temperature, wavelength, brightness, name, and pin numbers)
    queried by a list of plant ids. If no plant ids are given, returns all plants.

    Usage: plant_ids are given as a URL request parameter e.g. "?plant_ids=2,3,4" returns plants with ``id's`` 2,3 and
    4. Returns the plants' conditions as JSON.

    GET
    """
    # if plant_ids are passed in the request arguments, retrieve only those plants
    plant_ids = request.args.get('plant_ids')
    if plant_ids:
        plant_ids = plant_ids.split(',')
        plants = Plant.query.filter(Plant.id.in_(plant_ids)).all()
    else:
        # otherwise retrieve all plants
        plants = Plant.query.all()

    # if no plants are found, return 404
    if not plants:
        return abort(404, "No plants found")

    # serialize the plants and return them as a JSON response
    plants_json = [json_encoder(plant) for plant in plants]
    return jsonify(plants_json), 200


@plant_bp.route('/edit_plant/<int:plant_id>', methods=["PATCH"])
def edit_plant(plant_id):
    plant = Plant.query.get(plant_id)
    if not plant:
        abort(404, "Plant not found")
    data = request.json

    try:
        for key, value in data.items():
            setattr(plant, key, value)
        print(plant)
        db.session.commit()
        return jsonify({'message': 'Plant updated successfully'})
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, 'An error occurred while editing the plant')


@plant_bp.route('/update_conditions', methods=["PATCH"])
def update_conditions():
    pass


@plant_bp.route('/new_plant', methods=["POST"])
def new_plant():
    """
    Add a new single plant by specifying conditions. Use ``new_plants`` for multiple plants at once. Must specify all
    conditions except for ``name``, which is automatically generated if omitted.

    Usage: json body of request is used for specifying plant conditions e.g. "wavelength": 10 results in a new plant
    with  ``wavelength`` = 10

    POST
    """
    try:
        json = validate_json(request.json, (300, 800), (0, 35))  # validate json data sent in request
        plant = json_decoder(json)  # convert to Plant objects
        db.session.add(plant)  # add to database
        db.session.commit()
        return jsonify({'message': f'Successfully added new plant'}), 200
    except SQLAlchemyError:  # if error occurs during database process rollback and return 500
        db.session.rollback()
        abort(500, 'An error occurred while adding the new plant')
    except ValueError as e:
        print(e)
        abort(500, e)


@plant_bp.route('/new_plants', methods=["POST"])
def new_plants():
    """
    Add multiple plants at once by specifying conditions. Should only use for multi-addition but can still work for
    single addition (use ``new_plant`` instead). Must specify all conditions except for ``name``, which is automatically
    generated if omitted.

    Usage: json body must be a list of plants, each with their conditions. For specifications on what the body requires,
    see ``new_plant`` .

    POST
    """
    try:
        plant_json_list = [validate_json(i, (300, 800), (0, 35)) for i in request.json]  # validate json data
        plants = [json_decoder(plant_json) for plant_json in plant_json_list]  # convert to Plant objects
        db.session.add_all(plants)  # add to database
        db.session.commit()
        return jsonify({'message': f'Successfully added {len(plants)} new plants'}), 200
    except SQLAlchemyError:  # if error occurs during database process rollback and return 500
        db.session.rollback()
        abort(500, 'An error occurred while adding the new plant')
    except ValueError as e:  # return 500 and error if json fails validation
        abort(500, e)
        # will only return first error found


@plant_bp.route('/delete_plant/<int:plant_id>', methods=["DELETE"])
def delete_plant(plant_id):
    """
    Delete single plant by using plant id. Use ``delete_plants`` for multiple plants at once.

    Usage: plant id is given as part of url e.g. "/delete_plant/2" deletes plant with ``id`` = 2

    DELETE
    """
    plant = Plant.query.get(plant_id)  # find plant
    if not plant:  # if not found return 404
        abort(404, 'Plant not found')
    try:
        db.session.delete(plant)
        db.session.commit()
        return jsonify({'message': 'Plant deleted successfully'}), 200
    except SQLAlchemyError:  # if error occurs during deletion rollback and return 500
        db.session.rollback()
        abort(500, 'An error occurred while deleting the plant')


@plant_bp.route('/delete_plants', methods=["DELETE"])
def delete_plants():
    """
    Delete plants by using plant id. Should only use for multi-deletion but can still work for single deletion
    (use ``delete_plant`` instead).

    Usage: plant ids are given as part of URL query parameters e.g. "?plant_ids=2,3,4" deletes plants with ``id's``
    2,3 and 4.

    DELETE
    """
    # get the plant IDs to be deleted from the URL query parameters
    plant_ids = request.args.get('plant_ids', "").split(",")

    # if no plant IDs were provided, return a 400 Bad Request error
    if not plant_ids:
        abort(400, 'No plant ids provided')
    try:
        plants = Plant.query.filter(Plant.id.in_(plant_ids)).all()  # find all the plants with the given IDs
        if not plants:  # if no plants were found with the given IDs, return 404
            abort(404, 'No plants found')
        for plant in plants:  # delete plants from database
            db.session.delete(plant)
        db.session.commit()
        return jsonify({'message': f'Successfully deleted {len(plants)} plants'}), 200
    except SQLAlchemyError:  # if error occurs during deletion rollback and return 500
        db.session.rollback()
        abort(500, 'An error occurred while deleting plants')


# Example usage: set LED brightness to 50%
# ip_address = '192.168.1.100'
# command = 'led'
# arg = 50
# send_command(ip_address, command, arg)

# talk to rpi and get current conditions
    # TODO storage of information updated onto database, sql or mongodb?