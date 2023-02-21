from flask import Blueprint, render_template, url_for
import requests

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
def home():
    plants = requests.get(url_for("api.plant.get_plants", _external=True))
    if plants.status_code == 404:
        plants = []
    else:
        plants = plants.json
    # TODO dynamically update local storage, user login, and rpi status
    # TODO design rest of templates, and recheck page layout
    # TODO add clipart on cards on dashboard
    return render_template("home.html", plants=plants)


@dashboard_bp.route('/plant_conditions')
def plant_conditions():
    plants = None
    return render_template("plant_conditions.html")


@dashboard_bp.route('/imaging')
def imaging():
    return render_template("imaging.html")


@dashboard_bp.route('/images')
def images():
    return render_template("images.html")


@dashboard_bp.route('/settings')
def settings():
    return render_template("settings.html")
