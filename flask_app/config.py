import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = '736670cb10a600b695a55839ca3a5aa54a7d7356cdef815d2ad6e19a2031182b'
    AUTH_ENABLED = False

    DEFAULT_IDEAL_TEMPERATURE = 22.0
    DEFAULT_IDEAL_WAVELENGTH = 670
    DEFAULT_IDEAL_BRIGHTNESS = 100

    TEMPERATURE_BOUNDS = (0, 60)
    WAVELENGTH_BOUNDS = (300, 800)
    BRIGHTNESS_BOUNDS = (0, 100)

    RABBIT_USER = "rabbitmq"
    RABBIT_PASS = "rabbitmq"
    RABBIT_HOST = "rmq"
    RABBIT_PORT = 5672


class ProdConfig(Config):
    AUTH_ENABLED = True


class DevConfig(Config):
    DEBUG = True
