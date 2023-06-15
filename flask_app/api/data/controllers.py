from flask import request, Blueprint, current_app
from flask_restful import Resource
from ..models import Plant, create_plant, History, Images
from datetime import datetime
from fireo.utils import utils
from fireo.models import Model
from .. import rabbitmq

data_bp = Blueprint('data', __name__, url_prefix='/data')


class PlantResource(Resource):

    def get(self, plant_id=None):
        if not plant_id:
            plants = Plant.collection.fetch()
            return [plant.to_dict() for plant in plants]
        else:
            plant = Plant.collection.get(plant_id)
            if plant:
                return plant.to_dict()
            else:
                return {"error": "Plant not found"}, 404

    def post(self):
        try:
            data = request.get_json()
            plant = create_plant(
                name=data.get('name'),
                heating_element_pin=data.get('heating_element_pin'),
                multiplexer_channel=data.get('multiplexer_channel'),
                led_start_number=data.get('led_start_number'),
                ideal_temperature=data.get('ideal_temperature'),
                ideal_wavelength=data.get('ideal_wavelength'),
                ideal_brightness=data.get('ideal_brightness'),
            )
            plant.save()

            value = prepare_data(plant)
            message = f"new,{plant.id},{value}"
            try:
                response = rabbitmq.call("plant", message).decode()
                print(response)  # TODO add error handling on return
            except AttributeError:
                return {"message": f"Added plant {plant.id}, will update Raspberry Pi on launch."}, 201

            return {"message": f"Added plant {plant.id}."}, 201
        except ValueError as e:
            return {"error": e.__str__()}, 400

    def delete(self, plant_id):
        plant = Plant.collection.get(plant_id)
        if plant:
            Plant.collection.delete(id=plant_id)

            message = f"delete,{plant.id},"
            try:
                response = rabbitmq.call("plant", message).decode()
                print(response)  # TODO add error handling on return
            except AttributeError:
                return {"message": f"Plant deleted, will update Raspberry Pi on launch."}, 204

            return '', 204
        else:
            return {"error": "Plant not found."}, 404

    def patch(self, plant_id):
        try:
            plant = Plant.collection.get(plant_id)
            if not plant:
                return {"error": "Plant not found."}, 404

            data = request.get_json()
            fields = ['name', 'heating_element_pin', 'multiplexer_channel', 'led_start_number', 'ideal_temperature',
                      'ideal_wavelength', 'ideal_brightness']

            try:
                valid_data = validate_patch(data, fields, [
                    current_app.config.get("TEMPERATURE_BOUNDS"),
                    current_app.config.get("WAVELENGTH_BOUNDS"),
                    current_app.config.get("BRIGHTNESS_BOUNDS")
                ])
            except Exception as e:
                return e.__str__(), 400

            for field, value in valid_data.items():
                setattr(plant, field, value)

            plant.update()

            value = prepare_data(plant)
            message = f"update,{plant.id},{value}"
            try:
                response = rabbitmq.call("plant", message).decode()
                print(response)  # TODO add error handling on return
            except AttributeError:
                return {"message": f"Updated plant {plant_id}, will update Raspberry Pi on launch."}

            return {"message": f"Updated plant {plant_id}."}
        except ValueError as e:
            return {"error": e.__str__()}, 400

    def put(self, plant_id):
        try:
            plant = Plant.collection.get(plant_id)
            if not plant:
                return {"error": "Plant not found"}, 404
            data = request.get_json()

            # Check if all necessary fields are present
            required_fields = {'name', 'temperature_sensor_pin', 'heating_element_pin', 'led_pin'}
            if not all(field in data for field in required_fields):
                return {"error": "All required fields not provided for update"}, 400

            # Update fields
            plant.name = data['name']
            plant.temperature_sensor_pin = data['temperature_sensor_pin']
            plant.heating_element_pin = data['heating_element_pin']
            plant.led_pin = data['led_pin']
            plant.update()

            value = plant.to_dict()
            message = f"new,{plant.id},{value}"
            try:
                response = rabbitmq.call("plant", message).decode()
                print(response)  # TODO add error handling on return
            except AttributeError:
                return {"message": f"Updated plant {plant_id}, will update Raspberry Pi on launch."}

            return {"message": f"Updated plant {plant_id}."}
        except ValueError as e:
            return {"error": e.__str__()}, 400


class HistoryResource(Resource):

    def get(self, plant_id):
        plant = Plant.collection.get(plant_id)
        if not plant:
            return {"error": f"Plant {plant_id} doesn't exist."}, 404
        history = plant.history
        if not history:
            return []
        else:
            return [h.to_dict() for h in history]

    def post(self, plant_id):
        plant = Plant.collection.get(plant_id)
        if not plant:
            return {"error": f"Plant {plant_id} doesn't exist."}, 404
        data = request.get_json()
        new_history = History(
            temperature=data.get('temperature'),
            wavelength=data.get('wavelength'),
            brightness=data.get('brightness'),
            ideal_temperature=data.get('ideal_temperature'),
            ideal_wavelength=data.get('ideal_wavelength'),
            ideal_brightness=data.get('ideal_brightness'),
            date=datetime.fromisoformat(data.get('date')),
            parent=plant.key
        )
        if plant.history:
            plant.history.append(new_history)
        else:
            new_history.save()
        plant.update()
        return {"message": f"Added history to plant {plant_id}."}, 201

    def delete(self, plant_id, history_id):
        plant = Plant.collection.get(plant_id)
        history_key = utils.get_key("history", history_id, plant.key)
        history = History.collection.get(history_key)
        if not plant:
            return {"error": f"Plant {plant_id} doesn't exist."}, 404
        if history is None:
            return {"error": f"History {history_id} doesn't exist."}, 404

        # Delete the history object
        History.collection.delete(history_key)
        return "", 204


class ImagesResource(Resource):
    # TODO continue images endpoint

    def get(self, plant_id: str, images_id: str = None):
        plant = Plant.collection.get(plant_id)
        if not plant:
            return {"error": f"Plant {plant_id} doesn't exist."}, 404

        # specific image set
        if images_id:
            images_key = utils.get_key("images", images_id, plant.key)
            images = Images.collection.get(images_key)
            if images:
                return images.to_dict()
            else:
                return {"error": f"Images set with key {images_key} not found."}, 404

        # all image sets
        else:
            images = plant.images
            if images:
                return [i.to_dict() for i in images]
            return []


def validate_patch(data: dict, fields: list, bounds: list[tuple]):
    filtered_data = {field: data[field] for field in fields if field in data}

    fields_to_check_bounds = ['ideal_temperature', 'ideal_wavelength', 'ideal_brightness']
    out_of_bounds = check_bounds(fields_to_check_bounds, bounds, filtered_data)
    if out_of_bounds:
        raise ValueError(f"Fields out of bounds: {', '.join(out_of_bounds)}")

    return filtered_data


def check_bounds(fields_list: list, bounds_list: list[tuple], data: dict):
    return [field for field, bounds in zip(fields_list, bounds_list)
            if field in data and not bounds[0] <= data[field] <= bounds[1]]


def prepare_data(plant: Plant | Model):
    data = {
        plant.id: {
            "settings": {
                "heating_element_pin": plant.heating_element_pin,
                "multiplexer_channel": plant.multiplexer_channel,
                "led_start_number": plant.led_start_number,
            },
            "ideal": {
                "temperature": plant.ideal_temperature,
                "brightness": plant.ideal_brightness,
                "wavelength": plant.ideal_wavelength,
            }
        }
    }
    return str(data)
