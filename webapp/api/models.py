from .. import db


class Plant(db.Model):
    __tablename__ = "plants"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), default=f"Plant_id_{id}")
    temperature = db.Column(db.Float, nullable=False)
    wavelength = db.Column(db.Integer, nullable=False)
    brightness = db.Column(db.Integer, nullable=False)

    temperature_sensor_pin = db.Column(db.Integer, nullable=False, unique=True)
    heating_element_pin = db.Column(db.Integer, nullable=False, unique=True)
    led_red_pin = db.Column(db.Integer, nullable=False, unique=True)
    led_green_pin = db.Column(db.Integer, nullable=False, unique=True)
    led_blue_pin = db.Column(db.Integer, nullable=False, unique=True)

    def __repr__(self):
        return f"<Plant {self.id} '{self.name}' {self.temperature}°C {self.wavelength}nm {self.brightness}%>"


def json_encoder(plant: Plant) -> dict:
    json = {
        "id": plant.id,
        "name": plant.name,
        "wavelength": plant.wavelength,
        "brightness": plant.brightness,
        "temperature_sensor_pin": plant.temperature_sensor_pin,
        "heating_element_pin": plant.heating_element_pin,
        "led_red_pin": plant.led_red_pin,
        "led_blue_pin": plant.led_blue_pin,
        "led_green_pin": plant.led_green_pin
    }
    return json


def json_decoder(json: dict) -> Plant:
    plant = Plant(**json)
    return plant


def validate_json(data, wavelength_bounds: tuple, temperature_bounds: tuple) -> dict:
    name = data.get('name',)
    brightness = data.get('brightness')
    temperature = data.get('temperature')
    wavelength = data.get('wavelength')

    temperature_sensor_pin = data.get('temperature_sensor_pin')
    heating_element_pin = data.get('heating_element_pin')
    led_red_pin = data.get('led_red_pin')
    led_green_pin = data.get('led_green_pin')
    led_blue_pin = data.get('led_blue_pin')

    if not all([name, brightness, temperature, wavelength, temperature_sensor_pin, heating_element_pin, led_red_pin,
                led_green_pin, led_blue_pin]):
        raise ValueError('Missing required field')

    try:
        brightness = int(brightness)
        if not 0 <= brightness <= 100:
            raise ValueError(f'Brightness {brightness} is not within range {(0, 100)}')
    except ValueError:
        raise ValueError(f'Brightness {brightness} is not an integer')

    try:
        temperature = float(temperature)
        if not temperature_bounds[0] <= temperature <= temperature_bounds[1]:
            raise ValueError(f'Temperature {temperature} is not within range {temperature_bounds}')
    except ValueError:
        raise ValueError(f'Temperature {temperature} is not a float')

    try:
        wavelength = int(wavelength)
        if not wavelength_bounds[0] <= wavelength <= wavelength_bounds[1]:
            raise ValueError(f'Wavelength {wavelength} is not within range {wavelength_bounds}')
    except ValueError:
        raise ValueError(f'Wavelength {wavelength} is not an integer')

    try:
        temperature_sensor_pin = int(temperature_sensor_pin)
        heating_element_pin = int(heating_element_pin)
        led_red_pin = int(led_red_pin)
        led_green_pin = int(led_green_pin)
        led_blue_pin = int(led_blue_pin)
    except ValueError:
        raise ValueError('Pin values must be integers')
    return {
        'name': name,
        'brightness': brightness,
        'temperature': temperature,
        'wavelength': wavelength,
        'temperature_sensor_pin': temperature_sensor_pin,
        'heating_element_pin': heating_element_pin,
        'led_red_pin': led_red_pin,
        'led_green_pin': led_green_pin,
        'led_blue_pin': led_blue_pin
    }


@db.event.listens_for(db.session, 'after_commit')
def on_after_commit(session):
    print('A commit was just performed!')

# TODO define other event listeners here
