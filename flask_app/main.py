import os
from dotenv import load_dotenv
from api import create_app

load_dotenv()
env = os.environ.get('WEBAPP_ENV', 'dev')
app = create_app(f'config.{env.capitalize()}Config')


if __name__ == '__main__':
    app.run()

# TODO add error handling with wrong types
# TODO fix imaging endpoints and process requests properly on imaging rpi
# TODO figure out gphoto stuff
# TODO process requests properly on plant rpi
# TODO host on google cloud
# TODO write github readme
# TODO write docstrings for all classes + functions
# TODO write documentation with postman + other service for rest of documentation
# TODO write unit + coverage tests
# TODO finish docstrings and documentation on postman
