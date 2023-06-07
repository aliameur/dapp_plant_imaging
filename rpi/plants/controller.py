# import RPi.GPIO as GPIO
# from simple_pid import PID
import ast
import threading
import time


class Controller:

    def __init__(self):
        self.plants = {}
        self.threads = {}
        self.calibration = None  # TODO add calibration
        self.default_ideal = {
            "temperature": 25,
            "wavelength": 700,
            "brightness": 80
        }


    def init_plants(self, plant_dict: str) -> str:
        try:
            plant_dict = self._string_to_dict(plant_dict)
            self.plants = plant_dict
        except Exception as e:
            return e.__str__()

    def get_current_conditions(self, plant_id: str) -> str:
        if plant_id == 'all':
            # get all
            pass
        else:
            # get one
            pass

    def set_wavelength(self, plant_id: str, wavelength: int):
        pass

    def set_brightness(self, plant_id: str, brightness: int):
        pass

    def set_temperature(self, plant_id: str, temp: float):
        # Here you would update the setpoint of your PID controller
        self.plants[plant_id]["pid"].setpoint = temp
        # Then you would get the new control value and apply it to your heating element
        control_value = self.plants[plant_id]["pid"](temp)
        # TODO: GPIO call to control the heating element with the control_value
        self.plants[plant_id]["ideal"]["temperature"] = temp

    def new_plant(self, plant_id: str, data: str) -> str:
        try:
            data = self._string_to_dict(data)
            self.plants[plant_id] = {
                "settings": data,
                "ideal": self.default_ideal,
                "current": {},
                "pid": PID(1, 0.1, 0.05, setpoint=self.default_ideal["temperature"]),
                "running": True
            }
            t = threading.Thread(target=self._plant_loop, args=(plant_id,))
            t.start()
            self.threads[plant_id] = t
        except Exception as e:
            return e.__str__()

    def delete_plant(self, plant_id: str) -> str:
        try:
            self.plants[plant_id]["running"] = False
            self.threads[plant_id].join()
            del self.plants[plant_id]
            del self.threads[plant_id]
        except Exception as e:
            return e.__str__()

    def _plant_loop(self, plant_id: str):
        while self.plants[plant_id]["running"]:
            current_temp = self._read_temperature(plant_id)
            control_value = self.plants[plant_id]["pid"](current_temp)
            # TODO adjust heating element w/ control_value
            time.sleep(1)  # may need to adjust

    def _read_temperature(self, plant_id: str):
        # placeholder for now, replace with actual function to read temperature from sensor
        pass

    def to_dict(self) -> dict:
        return self.plants

    @staticmethod
    def _wavelength_to_rgb(wavelength: int) -> tuple:
        # use self.calibration to convert to rgb, placeholder for now
        rgb = (0, 0, 0)
        return rgb

    @staticmethod
    def _string_to_dict(string: str) -> dict:
        return ast.literal_eval(string)
