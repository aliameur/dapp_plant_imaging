# from controller import Controller
from simple_pid import PID
# import time
# import numpy as np

# Test duration and sample period
test_duration_sec = 10 * 60  # 10 minutes
sample_period_sec = 2
setpoint = 20
#
# controller = Controller()
# controller.plants = {
#     "1": {
#         "settings": {
#             "heating_element_pin": 23,
#             "multiplexer_channel": 0,
#             "led_start_number": 0,
#         },
#         "ideal": {
#             "temperature": setpoint,
#         },
#         "temperature_pid": PID(1, 0.1, 0.05, setpoint=setpoint),
#         "running": False
#     }
# }

temperatures = []
control_values = []

import random
import time
class Heater:
    def __init__(self, pin, active_high):
        self.temp = 5
        self.change = 2

    def on(self):
        print("turned heater on")
        self.temp += self.randomize_10_percent(self.change)

    def off(self):
        print("turned heater off")
        self.temp -= self.randomize_10_percent(self.change)

    def read_temp(self):
        return self.temp

    def randomize_10_percent(self, value):
        lower_bound = value * 0.9  # 10% less than the value
        upper_bound = value * 1.1  # 10% more than the value
        return random.uniform(lower_bound, upper_bound)



pid = PID(1, 0.1, 0.05, setpoint=setpoint)
heater = Heater(23, active_high=False)

while True:
    temp = heater.read_temp()
    print(f"temp: {round(temp, 2)}", end=" ")
    control = pid(temp)

    if control > 0:
        heater.on()
    else:
        heater.off()
    time.sleep(2)


#
# # Open the log file
# with open(f"{setpoint}C", "w") as log_file:
#     # Write the header line
#     log_file.write("Time,Temperature,ControlValue\n")
#
#     # Test loop
#     start_time = time.time()
#     while time.time() - start_time < test_duration_sec:
#         # Read the current temperature and control value
#         temp = controller.read_temperature("1")
#         control_value = controller.plants["1"]["temperature_pid"](temp)
#
#         # apply pid
#         controller.control_heating("1", control_value)
#
#         # Store them
#         temperatures.append(temp)
#         control_values.append(control_value)
#
#         # Write the current time, temperature, and control value to the log file
#         log_file.write(f"{round(time.time() - start_time, 2)},{temp},{control_value}\n")
#
#         # Wait for the next sample
#         time.sleep(sample_period_sec)
#
# # Compute the variance of the temperature and PID control values
# temp_variance = np.var(temperatures)
# control_variance = np.var(control_values)
#
# print(f"Temperature variance: {temp_variance}")
# print(f"Control value variance: {control_variance}")
