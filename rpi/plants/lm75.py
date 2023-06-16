from adafruit_tca9548a import TCA9548A_Channel
from functools import wraps


def retry_on_none(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(max_retries):
                result = func(*args, **kwargs)
                if result is not None:
                    return result
            return None

        return wrapper

    return decorator


# @retry_on_none()
def read_lm75(channel: TCA9548A_Channel):
    try:
        """Reads LM75 Temperature Sensor"""
        if not channel.try_lock():
            return None
        buffer = bytearray(2)  # Buffer to hold the 2 bytes read from the register
        channel.readfrom_into(0x48, buffer)

        # pack the bytes into a word manually
        raw_temp = (buffer[0] << 8) + buffer[1] & 0xFFFF
        temperature = (raw_temp / 32.0) / 8.0
        channel.unlock()
        return temperature
    except Exception:
        channel.unlock()
        raise ValueError
