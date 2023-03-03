import RPi.GPIO as GPIO


class Controller:

    def __init__(self):
        self.plants = {}
        self.calibration = None

    def init_plants(self, plant_dict: dict):
        self.plants = plant_dict

    def get_current_conditions(self, plant_id: int):
        pass

    def set_wavelength(self, plant_id: int, wavelength: int):
        pass

    def set_brightness(self, plant_id: int, brightness: int):
        pass

    def set_temp(self, plant_id: int, temp: float):
        pass

    def _wavelength_to_rgb(self, wavelength: int) -> tuple:
        # use self.calibration to convert to rgb
        rgb = ()
        return rgb

    def to_dict(self):
        pass
