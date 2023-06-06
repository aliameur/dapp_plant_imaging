from fireo.models import Model, NestedModel
from fireo.fields import TextField, NumberField, DateTime


class History(Model):
    temperature = NumberField()
    wavelength = NumberField()
    brightness = NumberField()
    date = DateTime()


class Plant(Model):
    name = TextField()
    temperature_sensor_pin = NumberField()
    heating_element_pin = NumberField()
    led_pin = NumberField()
    history = NestedModel(History)

    class Meta:
        missing_field = 'raise_error'
        to_lowercase = True
        collection_name = "plants"

    def validate_pins(self):
        print("temp", self.temperature_sensor_pin)
        print("heat", self.heating_element_pin)
        print("led", self.led_pin)
        if len({self.temperature_sensor_pin, self.heating_element_pin, self.led_pin}) != 3:
            raise ValueError("Pins must be unique")


def create_plant(name, temperature_sensor_pin, heating_element_pin, led_pin):
    if len({temperature_sensor_pin, heating_element_pin, led_pin}) != 3:
        raise ValueError("Pins must be unique")
    plant = Plant(
        name=name,
        temperature_sensor_pin=temperature_sensor_pin,
        heating_element_pin=heating_element_pin,
        led_pin=led_pin
    )
    if not plant.name:
        plant.name = f'Plant {plant.key.split("/")[1]}'
    return plant
