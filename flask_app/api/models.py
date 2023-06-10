from fireo.models import Model, NestedModel
from fireo.fields import TextField, NumberField, DateTime, ListField
from flask import current_app


class History(Model):
    temperature = NumberField()
    wavelength = NumberField()
    brightness = NumberField()
    date = DateTime()


class Images(Model):
    date = DateTime()
    type = TextField()
    raw_images = ListField()
    laplacian_images = ListField()
    focus_stacked = TextField()


class Plant(Model):
    name = TextField()
    heating_element_pin = NumberField()
    multiplexer_channel = NumberField()
    led_start_number = NumberField()

    history = NestedModel(History)
    images = NestedModel(Images)

    ideal_temperature = NumberField()
    ideal_wavelength = NumberField()
    ideal_brightness = NumberField()

    class Meta:
        missing_field = 'raise_error'
        to_lowercase = True
        collection_name = "plants"


def create_plant(name=None, heating_element_pin=None, multiplexer_channel=None,
                 led_start_number=None, ideal_temperature=None, ideal_wavelength=None,
                 ideal_brightness=None) -> Plant:
    if heating_element_pin is None or multiplexer_channel is None or led_start_number is None:
        raise ValueError('Heating_element_pin, multiplexer_channel, and led_start_number must be provided.')

    plant = Plant(
        name=name,
        heating_element_pin=heating_element_pin,
        multiplexer_channel=multiplexer_channel,
        led_start_number=led_start_number,
        ideal_temperature=ideal_temperature if ideal_temperature is not None else
        current_app.config.get("DEFAULT_IDEAL_TEMPERATURE"),
        ideal_wavelength=ideal_wavelength if ideal_wavelength is not None else
        current_app.config.get("DEFAULT_IDEAL_WAVELENGTH"),
        ideal_brightness=ideal_brightness if ideal_brightness is not None else
        current_app.config.get("DEFAULT_IDEAL_BRIGHTNESS"),
    )
    if not plant.name:
        plant.name = f'Plant {plant.key.split("/")[1]}'
    return plant
