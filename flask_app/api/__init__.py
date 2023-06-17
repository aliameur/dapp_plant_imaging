from flask import Flask
from flask_cors import CORS
from .rabbitmq import RabbitMQ
from firebase_admin import initialize_app
from .models import Plant
from pika.exceptions import ConnectionBlockedTimeout

rabbitmq = RabbitMQ()
cors = CORS()


def create_app(object_name):
    """
    A flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object,
                     e.g. project.config.ProdConfig
    """
    app = Flask(__name__)
    app.config.from_object(object_name)
    app.url_map.strict_slashes = False

    rabbitmq.init_app(app)
    cors.init_app(app)
    initialize_app()

    from .plants import create_module as plants_create_module
    from .imaging import create_module as imaging_create_module
    from .data import create_module as data_create_module
    from .auth import create_module as auth_create_module

    plants_create_module(app)
    imaging_create_module(app)
    data_create_module(app)
    auth_create_module(app)

    @app.route('/init')
    def init():
        plants = Plant.collection.fetch()
        data = prepare_all_data(plants)
        message = f"init,,{data}"
        print(data)
        try:
            response = rabbitmq.call("plant", message).decode()
            print(response)
        except ConnectionBlockedTimeout:
            return {"error": "Timeout occurred"}, 500
        except Exception as e:
            return {"error": e}, 500

    def prepare_all_data(plants):
        combined_data = {}
        for plant in plants:
            combined_data[plant.id] = {
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
        return str(combined_data)

    return app
