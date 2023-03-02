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
    Get all attributes and ideal conditions for a single plant by querying it using its unique plant ID.

    Usage:
    Send a GET request to /plants/<int:plant_id> endpoint.

    Raises:
    404 Error - If the plant with the specified ID does not exist in the database.

    :return: A JSON object containing the plant's name, pins, temperature, wavelength, and brightness.
    """
    plant = Plant.query.get(plant_id)
    if not plant:
        abort(404, "Plant not found")
    plant_json = plant.to_dict()  # return result as json
    return plant_json


@plants_bp.route('/')
def get_plants():
    """
    Get the latest available conditions for multiple plants (temperature, wavelength, brightness, name, and pins)
    queried by a list of plant ids. If no plant ids are given, returns all plants.

    Usage: Send a GET request to /plants/ endpoint. If you want to retrieve data for specific plants only, pass
    their ids as comma-separated values in the `plant_ids` query parameter, which will return all plants with matching
    ids. If no `plant_ids` parameter is passed, all available plants will be returned.

    Raises:
    404 Error - If the plants with the specified IDs does not exist in the database.

    :return: A JSON response containing the latest conditions for the requested plants.
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
    """
    Update attributes of a single plant by using plant id.

    Usage: Send a PATCH request to /plants/<plant_id> endpoint where <plant_id> is the id of the plant you want to edit.
    The request body should contain a JSON object with the new attributes for the plant. Any attributes not specified in
    the JSON object will remain unchanged.

    Raises:
    404 Error - If the plant with the specified ID does not exist in the database.
    500 Error - If an error occurs while editing the plant

    :return: A JSON response indicating the success of the edit operation.
    """
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
    Add a new plant or multiple plants to the database with specified attributes and ideal conditions. If a single plant
    is to be added, all attributes and ideal conditions except for ``name`` must be specified, since the name will be
    automatically generated if omitted. For multiple plants, send a list of plant conditions in the request body.

    Usage: Send a POST request to /plants/ endpoint with a JSON body containing the attributes and ideal conditions for
    the plant(s) to be added. To add a single plant, specify the attributes directly in the JSON body. To add multiple
    plants, send a list of plant attributes. Plant attributes include: name, temperature sensor pin, heating element
    pin, wavelength, temperature, and brightness.

    Raises:
    500 Error - If the request is not valid, or an error occurs while adding the new plant(s) to the database.

    :return: A JSON response indicating the success or failure of the request.
    """
    if isinstance(request.json, dict):
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
    Delete a single plant by its unique plant ID.

    Usage: To delete a single plant, send a DELETE request to /plants/<int:plant_id>. The plant's unique ID must be
    included in the URL as a parameter. For example, "/plants/2" will delete the plant with ID 2.

    Raises:
    404 Error - If the plant with the specified ID does not exist in the database.

    :return: A JSON response containing a message indicating that the plant was successfully deleted.
    """
    plant = Plant.query.get(plant_id)  # find plant
    if not plant:  # if not found return 404
        abort(404, 'Plant not found')
    try:
        db.session.delete(plant)
        db.session.commit()
        return jsonify({'message': 'Plant deleted successfully'}), 200  # TODO return 200 or 204
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
