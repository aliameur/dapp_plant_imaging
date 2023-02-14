from flask import Flask
from flask_bootstrap import Bootstrap5
from api import api_bp
from user import user_bp

app = Flask(__name__)
bootstrap = Bootstrap5(app)

app.register_blueprint(api_bp)
app.register_blueprint(user_bp)

if __name__ == '__main__':
    app.run(debug=True)
