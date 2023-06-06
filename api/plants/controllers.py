from flask import Blueprint, request, current_app
from .. import rabbitmq
from pika.exceptions import ConnectionBlockedTimeout
from flask_restful import Resource

plants_bp = Blueprint('plants', __name__, url_prefix='/plants')


# TODO write RPI script for controlling of led and temperature
# TODO finish docstrings and documentation on postman
# TODO fix rpi board communication and error handling if communication goes bad


class ConditionResource(Resource):

    def get(self, plant_id=None):
        if plant_id:
            message = f"get,{plant_id},"
        else:
            message = f"get,all,"
        try:
            plant_conditions = rabbitmq.call("plant", message).decode()
            if plant_conditions != "plant does not exist":
                return plant_conditions
            else:
                return {"error": "Plant requested does not exist."}, 404
        except ConnectionBlockedTimeout:
            return {"error": "Timeout occurred"}, 500
        except Exception as e:
            return {"error": e}, 500

    def post(self, plant_id=None):
        if plant_id:
            try:
                data = request.get_json()
                data = validate_and_format_post_data(data, ["temperature", "wavelength", "brightness"], [
                    current_app.config.get("TEMPERATURE_BOUNDS"),
                    current_app.config.get("WAVELENGTH_BOUNDS"),
                    current_app.config.get("BRIGHTNESS_BOUNDS"),
                ])

                for key, val in data.items():
                    message = f"{plant_id},{key},{val}"
                    response = rabbitmq.call("plant", message)
                    if response == "plant does not exist":
                        return {"error": "Plant requested does not exist"}, 404
                return {"message": f"Updated all conditions for plant {plant_id}"}, 201
            except ValueError as e:
                return {"error": e.__str__()}, 400
            except ConnectionBlockedTimeout:
                return {"error": "Timeout occurred"}, 500
            except Exception as e:
                return {"error": e.__str__()}, 500
        else:
            return {"error": "No plant_id specified."}, 400

    def patch(self, plant_id=None):
        if plant_id:
            try:
                data = request.get_json()
                data = validate_and_format_patch_data(data, ["temperature", "wavelength", "brightness"], [
                    current_app.config.get("TEMPERATURE_BOUNDS"),
                    current_app.config.get("WAVELENGTH_BOUNDS"),
                    current_app.config.get("BRIGHTNESS_BOUNDS"),
                ])
                response, code = send_messages(data, plant_id)
                if code == 404:
                    return response, code
                else:
                    return {"message": f"Updated conditions for plant {plant_id}"}, 201
            except ValueError as e:
                return {"error": e.__str__()}, 400
            except ConnectionBlockedTimeout:
                return {"error": "Timeout occurred"}, 500
            except Exception as e:
                return {"error": e.__str__()}, 500
        else:
            return {"error": "No plant_id specified."}, 400


def validate_and_format_post_data(data: dict, required_fields: list, required_bounds: list[tuple]):
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    out_of_bounds = core_validate(required_fields, required_bounds, data)
    if out_of_bounds:
        raise ValueError(f"Fields out of bounds: {', '.join(out_of_bounds)}")
    return {field: data[field] for field in required_fields}


def validate_and_format_patch_data(data: dict, required_fields: list, required_bounds: list[tuple]):
    present_fields = [field for field in required_fields if field in data]

    out_of_bounds = core_validate(present_fields, required_bounds, data)
    if out_of_bounds:
        raise ValueError(f"Fields out of bounds: {', '.join(out_of_bounds)}")
    return {field: data[field] for field in present_fields}


def core_validate(fields_list: list, bounds_list: list[tuple], data: dict):
    return [field for field, bounds in zip(fields_list, bounds_list)
            if not bounds[0] <= data[field] <= bounds[1]]


def send_messages(data, plant_id):
    for key, val in data.items():
        message = f"{plant_id},{key},{val}"
        response = rabbitmq.call("plant", message)
        if response == "plant does not exist":
            return {"error": "Plant requested does not exist"}, 404
    return "", 200
