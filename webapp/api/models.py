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


def json_encoder(model: Plant) -> dict:
    json = {
        "id": model.id,
        "name": model.name,
        "wavelength": model.wavelength,
        "brightness": model.brightness,
        "temperature": model.temperature
    }
    return json
