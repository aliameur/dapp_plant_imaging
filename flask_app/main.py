import os
from dotenv import load_dotenv
from api import create_app

load_dotenv()
env = os.environ.get('WEBAPP_ENV', 'dev')
app = create_app(f'config.{env.capitalize()}Config')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

# TODO add error handling with wrong types (later, minor change)
# TODO fix imaging endpoints and process requests properly on imaging rpi
# TODO figure out gphoto stuff
# TODO process requests properly on plant rpi
# TODO host on google cloud
# TODO write github readme
# TODO write docstrings for all classes + functions
# TODO write documentation with postman + other service for rest of documentation
# TODO write unit + coverage tests
# TODO finish docstrings and documentation on postman

# TODO write plant rpi code 30 min
# TODO handle responses sent back 30 min TODAY 1 hr
# TODO write connection to the rabbitmq code correctly on rpi
# TODO finish up the dashboard
