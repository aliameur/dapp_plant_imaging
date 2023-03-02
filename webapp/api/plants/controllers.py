from flask import Blueprint, jsonify, request, current_app, abort
from ..models import db, Plant, validate_json
from sqlalchemy.exc import SQLAlchemyError
from ... import rabbitmq
from pika.exceptions import ConnectionBlockedTimeout

plants_bp = Blueprint('plants', __name__, url_prefix='/plants')
# TODO finish docstrings and documentation on postman
# TODO write RPI script for controlling of led and temperature
# TODO write fetch conditions request error handling
# TODO finish docstrings and documentation on postman


@plants_bp.route('/<int:plant_id>')
def get_plant(plant_id):
    """
    Get all attributes and ideal conditions for a single plant () the latest available conditions for a single plant (temperature, wavelength, brightness, name, and pin numbers),
    queried by plant id.

    Usage: plant_id is given as a URL request parameter. Returns the plant conditions as JSON.

    GET
    """
    plant = Plant.query.get(plant_id)
    if not plant:
        abort(404, "Plant not found")
    plant_json = plant.to_dict()  # return result as json
    return plant_json


@plants_bp.route('/')
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
    plants_json = [plant.to_dict() for plant in plants]
    return jsonify(plants_json), 200


@plants_bp.route('/<int:plant_id>', methods=["PATCH"])
def edit_plant(plant_id):
    plant = Plant.query.get(plant_id)
    if not plant:
        abort(404, "Plant not found")

    try:
        data = validate_json(request.json,
                             current_app.config.get("WAVELENGTH_BOUNDS"),
                             current_app.config.get("TEMPERATURE_BOUNDS"),
                             edit=True)  # validate json data sent in request
        for key, value in data.items():  # update plant attributes
            setattr(plant, key, value)
        db.session.commit()
        return jsonify({'message': 'Plant updated successfully'}), 200
    except SQLAlchemyError:
        db.session.rollback()
        abort(500, 'An error occurred while editing the plant')
    except ValueError as e:
        abort(500, e)


@plants_bp.route('/', methods=["POST"])
def new_plant():
    """
    Add a new single plant by specifying conditions. Use ``new_plants`` for multiple plants at once. Must specify all
    conditions except for ``name``, which is automatically generated if omitted.

    Usage: json body of request is used for specifying plant conditions e.g. "wavelength": 10 results in a new plant
    with  ``wavelength = 10``

    POST
    """
    if not isinstance(request.json, list):
        try:
            json = validate_json(request.json,
                                 current_app.config.get("WAVELENGTH_BOUNDS"),
                                 current_app.config.get("TEMPERATURE_BOUNDS"))  # validate json data sent in request
            plant = Plant(**json)  # convert to Plant objects
            db.session.add(plant)  # add to database
            db.session.commit()
            return jsonify({'message': f'Successfully added new plant'}), 200
        except SQLAlchemyError:  # if error occurs during database process rollback and return 500
            db.session.rollback()
            abort(500, 'An error occurred while adding the new plant')
        except ValueError as e:
            abort(500, e)
    else:
        try:
            plant_json_list = [validate_json(i,
                                             current_app.config.get("WAVELENGTH_BOUNDS"),
                                             current_app.config.get("TEMPERATURE_BOUNDS"))
                               for i in request.json]  # validate json data
            plants = [Plant(**plant_json) for plant_json in plant_json_list]  # convert to Plant objects
            db.session.add_all(plants)  # add to database
            db.session.commit()
            return jsonify({'message': f'Successfully added {len(plants)} new plants'}), 200
        except SQLAlchemyError:  # if error occurs during database process rollback and return 500
            db.session.rollback()
            abort(500, 'An error occurred while adding the new plant')
        except ValueError as e:  # return 500 and error if json fails validation
            abort(500, e)
            # will only return first error found


@plants_bp.route('/<int:plant_id>', methods=["DELETE"])
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


@plants_bp.route('/<int:plant_id>/conditions')
def conditions(plant_id):
    plant = Plant.query.get(plant_id)
    if not plant:
        return abort(404, "Plant not found")

    try:  # TODO add error handling if no communication (bad connection) or other failure
        plant_conditions = rabbitmq.call(f"get,{plant_id}")
    except ConnectionBlockedTimeout:
        return abort(500, "Timeout occured")
    except Exception as e:
        return abort(500, e)
    return jsonify(plant_conditions), 200


# Example usage: set LED brightness to 50%
# ip_address = '192.168.1.100'
# command = 'led'
# arg = 50
# send_command(ip_address, command, arg)

# talk to rpi and get current conditions
# TODO storage of information updated onto database, sql or mongodb?
