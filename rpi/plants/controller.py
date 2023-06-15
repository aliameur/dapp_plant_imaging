import gpiozero
from simple_pid import PID
import ast
import threading
import time
import board
import neopixel
from adafruit_tca9548a import TCA9548A
from adafruit_bh1750 import BH1750
from lm75 import read_lm75

MUX_ADDRESS = 0x70
LIGHT_SENSOR_ADDRESS = 0x23
TEMP_SENSOR_ADDRESS = 0x48
MUX = TCA9548A(board.I2C())

TEMP_Kp = 1
TEMP_Ki = 0.1
TEMP_Kd = 0.05
BRIGHTNESS_Kp = 1
BRIGHTNESS_Ki = 0.1
BRIGHTNESS_Kd = 0.05


# time per loop of 10 secs?
# TODO convert from lux to brightness, need to test sensors
# TODO check if control loop works correctly
# TODO check type casting on setting methods
# TODO redo message handler to reflect current updates


class Controller:

    def __init__(self, led_board_pin: int = 18, n_leds: int = 48):
        self.plants = {}
        self.threads = {}
        self.calibration = None  # TODO add calibration
        led_pin = getattr(board, 'D' + str(led_board_pin))
        self.led_strip = neopixel.NeoPixel(led_pin, n_leds, auto_write=False)

    def init_plants(self, plants_dict: str) -> str:
        try:
            plants_dict = self._string_to_dict(plants_dict)
            self.plants = plants_dict
            for plant_id, plant in plants.items():
                self.init_plant(plant, plant_id)
            return "Successfully initialized all plants."
        except Exception as e:
            return e.__str__()

    def init_plant(self, plant: dict, plant_id: str):
        plant["temperature_pid"] = PID(TEMP_Kp, TEMP_Ki, TEMP_Kd,
                                       setpoint=plant["ideal"]["temperature"])
        plant["brightness_pid"] = PID(BRIGHTNESS_Kp, BRIGHTNESS_Ki, BRIGHTNESS_Kd,
                                      setpoint=plant["ideal"]["brightness"])
        plant["heater"] = gpiozero.OutputDevice(plant["settings"]["heating_element_pin"], active_high=False)
        plant["running"] = True

        self.set_wavelength(plant_id, plant["ideal"]["wavelength"], rewrite=False)

        t = threading.Thread(target=self._control_loop, args=(1, plant_id))
        t.start()
        self.threads[plant_id] = t

    def get_current_conditions(self, plant_id: str) -> str:
        if plant_id == 'all':
            data = self.extract_current(self.plants)
            return str(data)
        else:
            data = self.extract_current_single(self.plants[plant_id], plant_id)
            return str(data)

    def set_wavelength(self, plant_id: str, wavelength: int, rewrite=True):
        if rewrite:
            self.plants[plant_id]["ideal"]["wavelength"] = wavelength
        brightness = self.plants[plant_id]["ideal"]["brightness"]
        led_start = self.plants[plant_id]["settings"]["led_start_number"]

        rgb = self.wavelength_to_rgb(wavelength)
        self.led_strip[led_start: led_start + 6] = 6 * self.adjust_brightness(rgb, brightness)
        self.led_strip.show()

    def set_brightness(self, plant_id: str, brightness: int):
        self.plants[plant_id]["ideal"]["brightness"] = brightness
        self.plants[plant_id]["brightness_pid"].setpoint = brightness

    def set_temperature(self, plant_id: str, temp: float):
        self.plants[plant_id]["ideal"]["temperature"] = temp
        self.plants[plant_id]["temperature_pid"].setpoint = temp

    def new_plant(self, plant_id: str, data: str) -> str:
        try:
            plant_dict = self._string_to_dict(data)
            self.plants[plant_id] = plant_dict
            self.init_plant(self.plants[plant_id], plant_id)
            return f"Successfully added plant {plant_id}"
        except Exception as e:
            return e.__str__()

    def delete_plant(self, plant_id: str) -> str:
        try:
            self.plants[plant_id]["running"] = False
            self.threads[plant_id].join()
            del self.plants[plant_id]
            del self.threads[plant_id]
            return f"Successfully deleted plant {plant_id}."
        except Exception as e:
            return e.__str__()

    def read_temperature(self, plant_id: str) -> float:
        mux_channel = self.plants[plant_id]["multiplexer_channel"]
        return read_lm75(mux_channel)

    def read_brightness(self, plant_id: str) -> float:
        mux_channel = self.plants[plant_id]["multiplexer_channel"]
        sensor = BH1750(MUX[mux_channel])
        return sensor.lux

    def control_heating(self, plant_id: str, control_value: float):
        heater = self.plants[plant_id]['heater']
        if control_value > 0:
            heater.on()
        else:
            heater.off()

    def control_led(self, plant_id: str, brightness: float):

        start = self.plants[plant_id]["settings"]["led_start_number"]
        rgb = self.wavelength_to_rgb(self.plants[plant_id]["ideal"]["wavelength"])

        rgb_adjusted = self.adjust_brightness(rgb, brightness)

        self.led_strip[start:start + 6] = rgb_adjusted * 6
        self.led_strip.show()

    def _control_loop(self, time_per_loop: int, plant_id: str):
        while self.plants[plant_id]["running"]:
            current_temperature = self.read_temperature(self.plants[plant_id])  # in C
            current_brightness = self.read_brightness(self.plants[plant_id])  # in lux

            self.plants["plant_id"]["current"]["temperature"] = current_temperature
            self.plants["plant_id"]["current"]["brightness"] = current_brightness

            temperature_control_value = self.plants[plant_id]["temperature_pid"](current_temperature)
            brightness_control_value = self.plants[plant_id]["brightness_pid"](current_brightness)

            self.control_heating(plant_id, temperature_control_value)
            self.control_led(plant_id, brightness_control_value)

            time.sleep(time_per_loop)

    def to_dict(self) -> dict:
        return self.plants

    @staticmethod
    def wavelength_to_rgb(wavelength):
        gamma = 0.80
        intensity_max = 255
        factor, red, green, blue = 0.0, 0, 0, 0

        wavelength = float(wavelength)

        if 380 <= wavelength < 440:
            red = -(wavelength - 440) / (440 - 380)
            blue = 1.0
        elif 440 <= wavelength < 490:
            green = (wavelength - 440) / (490 - 440)
            blue = 1.0
        elif 490 <= wavelength < 510:
            green = 1.0
            blue = -(wavelength - 510) / (510 - 490)
        elif 510 <= wavelength < 580:
            red = (wavelength - 510) / (580 - 510)
            green = 1.0
        elif 580 <= wavelength < 645:
            red = 1.0
            green = -(wavelength - 645) / (645 - 580)
        elif 645 <= wavelength <= 780:
            red = 1.0

        # Let the intensity fall off near the vision limits
        if 380 <= wavelength < 420:
            factor = 0.3 + 0.7 * (wavelength - 380) / (420 - 380)
        elif 420 <= wavelength <= 700:
            factor = 1.0
        elif 700 < wavelength <= 780:
            factor = 0.3 + 0.7 * (780 - wavelength) / (780 - 700)

        # Don't want 0^x = 1 for x <> 0
        rgb = (0 if red == 0.0 else int(round(intensity_max * ((red * factor) ** gamma))),
               0 if green == 0.0 else int(round(intensity_max * ((green * factor) ** gamma))),
               0 if blue == 0.0 else int(round(intensity_max * ((blue * factor) ** gamma))))

        return rgb

    @staticmethod
    def adjust_brightness(rgb, brightness):
        return tuple(round(brightness * component) for component in rgb)

    @staticmethod
    def _string_to_dict(string: str) -> dict:
        return ast.literal_eval(string)

    @staticmethod
    def extract_current(data: dict):
        result = {}
        for key, value in data.items():
            result[key] = value["current"]
        return result

    @staticmethod
    def extract_current_single(data: dict, key: str):
        return {key: data["current"]}


# EXAMPLE PLANT
plants = {
    "id": {
        "settings": {
            "heating_element_pin": 1,
            "multiplexer_channel": 1,
            "led_start_number": 1,
        },
        "ideal": {
            "temperature": 10,
            "brightness": 10,
            "wavelength": 10,
        },
        "current": {
            "temperature": 10,
            "brightness": 10,
            "wavelength": 10,
        },
        "temperature_pid": PID(1, 0.1, 0.05, setpoint=15),
        "brightness_pid": PID(1, 0.1, 0.05, setpoint=15),
        "running": True
    }
}
