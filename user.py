from flask import Blueprint, render_template

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/')
def home():
    # return main page
    # jinja templating
    # one page app
    # create a
    return render_template("index.html")
