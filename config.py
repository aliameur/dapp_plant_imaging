import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = '736670cb10a600b695a55839ca3a5aa54a7d7356cdef815d2ad6e19a2031182b'


class ProdConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True
    PLANT_IP_ADDRESS = os.environ["IP_ADDRESS"]
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
