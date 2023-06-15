import time
from adafruit_tca9548a import TCA9548A
from adafruit_bh1750 import BH1750
import board

# LM75_ADDRESS could be 0x48, 0x49, 0x4A, 0x4B, etc., depending on the configuration of your sensor.
LM75_ADDRESS = 0x48

# If you're using another variant of the LM75, this register address might be different. Check the datasheet.
LM75_TEMP_REGISTER = 0
mux = TCA9548A(board.I2C())


def read_temp(tca_channel):
    if not channel.try_lock():
        return None
    buffer = bytearray(2)  # Buffer to hold the 2 bytes read from the register
    tca_channel.readfrom_into(LM75_ADDRESS, buffer)

    # pack the bytes into a word manually
    raw_temp = (buffer[0] << 8) + buffer[1] & 0xFFFF
    temperature = (raw_temp / 32.0) / 8.0
    tca_channel.unlock()
    return temperature


# Assuming tca_channel is an instance of TCA9548A_Channel
for i in [0, 3, 4, 5, 6, 7]:
    start = time.time()
    channel = mux[i]
    a = read_temp(channel)
    t = time.time()
    print(a, f'took {t - start}s')
    light_sensor = BH1750(channel)
    l = light_sensor.lux
    f = time.time()
    print(l, f'took {f - t}s')

import board
from gpiozero import OutputDevice, LED
import time

pins = [23, 24, 25, 12, 16, 5, 6, 13]

heaters = []
heater = LED(24)
heater.off
time.sleep(200000)

print('test')

for i in pins:
    h = OutputDevice(i, active_high=False)
    h.on()
    heaters.append(h)

while True:
    pass


import board
import neopixel
import time

pixels = neopixel.NeoPixel(board.D18, 48)

pixels.fill((0,255,0))
time.sleep(2)
pixels.deinit()
