import os
from dotenv import load_dotenv
from api import create_app

load_dotenv()
env = os.environ.get('WEBAPP_ENV', 'dev')
app = create_app(f'config.{env.capitalize()}Config')


if __name__ == '__main__':
    app.run()
