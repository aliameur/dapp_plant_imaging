from .. import db
from types import NoneType


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

    __table_args__ = (
        db.UniqueConstraint('temperature_sensor_pin', 'heating_element_pin', 'led_red_pin', 'led_green_pin',
                            'led_blue_pin', name='unique_plant'),
    )

    def __repr__(self):
        return f"<Plant {self.id} '{self.name}' {self.temperature}°C {self.wavelength}nm {self.brightness}%>"

    def to_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def json_decoder(json: dict) -> Plant:
    plant = Plant(**json)
    return plant


def validate_json(data, wavelength_bounds: tuple, temperature_bounds: tuple, edit=False) -> dict:
    name = data.get('name',)
    brightness = data.get('brightness')
    temperature = data.get('temperature')
    wavelength = data.get('wavelength')

    temperature_sensor_pin = data.get('temperature_sensor_pin')
    heating_element_pin = data.get('heating_element_pin')
    led_red_pin = data.get('led_red_pin')
    led_green_pin = data.get('led_green_pin')
    led_blue_pin = data.get('led_blue_pin')

    if not edit:
        if not all([name, brightness, temperature, wavelength, temperature_sensor_pin, heating_element_pin, led_red_pin,
                    led_green_pin, led_blue_pin]):
            raise ValueError('Missing required field')

    # validate brightness
    if brightness:
        try:
            brightness = int(brightness)
            if not 0 <= brightness <= 100:
                raise ValueError(f'Brightness {brightness} is not within range {(0, 100)}')
        except ValueError:
            raise ValueError(f'Brightness {brightness} is not an integer')

    # validate temperature
    if temperature:
        try:
            temperature = float(temperature)
            if not temperature_bounds[0] <= temperature <= temperature_bounds[1]:
                raise ValueError(f'Temperature {temperature} is not within range {temperature_bounds}')
        except ValueError:
            raise ValueError(f'Temperature {temperature} is not a float')

    # validate wavelength
    if wavelength:
        try:
            wavelength = int(wavelength)
            if not wavelength_bounds[0] <= wavelength <= wavelength_bounds[1]:
                raise ValueError(f'Wavelength {wavelength} is not within range {wavelength_bounds}')
        except ValueError:
            raise ValueError(f'Wavelength {wavelength} is not an integer')

    # validate PINS
    if all([temperature_sensor_pin, heating_element_pin, led_red_pin, led_green_pin, led_blue_pin]):
        try:
            temperature_sensor_pin = int(temperature_sensor_pin)
            heating_element_pin = int(heating_element_pin)
            led_red_pin = int(led_red_pin)
            led_green_pin = int(led_green_pin)
            led_blue_pin = int(led_blue_pin)
        except ValueError:
            raise ValueError('Pin values must be integers')

    if not edit:
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
    else:
        return {name: value for name, value in locals().items() if not isinstance(value, (bool, dict, tuple, NoneType))}


@db.event.listens_for(db.session, 'after_commit')
def on_after_commit(session):
    print('A commit was just performed!')

# TODO define other event listeners here
