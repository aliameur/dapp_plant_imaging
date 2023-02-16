from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
def home():
    # return main page
    # jinja templating
    # one page app
    # create a
    # TODO design the template to a satisfactory extent
    # TODO add jinja templating to call from api
    return render_template("home.html")
