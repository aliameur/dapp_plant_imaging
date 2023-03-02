import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = '736670cb10a600b695a55839ca3a5aa54a7d7356cdef815d2ad6e19a2031182b'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
    TEMPERATURE_BOUNDS = (0, 60)
    WAVELENGTH_BOUNDS = (300, 800)

    RABBIT_USER = "rabbitmq"
    RABBIT_PASS = "rabbitmq"
    RABBIT_HOST = "localhost"
    RABBIT_PORT = 5672


class ProdConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    PLANT_IP_ADDRESS = os.environ["IP_ADDRESS"]
    DASHBOARD_PRESENT = True
