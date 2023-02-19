from .. import db


class Plant(db.Model):
    __tablename__ = "plant_table"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), default=id)
    temperature = db.Column(db.Float)
    wavelength = db.Column(db.Integer)
    brightness = db.Column(db.Integer)

    def __repr__(self):
        return f"<Plant {self.id} '{self.name}' {self.temperature}°C {self.wavelength}nm {self.brightness}%>"


def json_encoder(plant: Plant) -> dict:
    json = {
        "id": plant.id,
        "name": plant.name,
        "wavelength": plant.wavelength,
        "brightness": plant.brightness,
        "temperature": plant.temperature
    }
    return json


def json_decoder(json: dict) -> Plant:
    plant = Plant(**json)
    # plant = Plant(name=json.get("name"),
    #               temperature=json.get("temperature"),
    #               wavelength=json.get("wavelength"),
    #               brightness=json.get("brightness")
    #               )
    return plant


def validate_json(data, wavelength_bounds: tuple, temperature_bounds: tuple) -> dict:
    name = data.get('name',)
    brightness = data.get('brightness')
    temperature = data.get('temperature')
    wavelength = data.get('wavelength')

    if not brightness or not temperature or not wavelength:
        raise ValueError('Missing required field')

    try:
        brightness = int(brightness)
        if not 0 <= brightness <= 100:
            raise ValueError(f'Brightness {brightness} is not within range {brightness_bounds}')
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

    return {
        'name': name,
        'brightness': brightness,
        'temperature': temperature,
        'wavelength': wavelength
    }