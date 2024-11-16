from flask import Blueprint

vehicle_registration_bp = Blueprint('vehicle_registration', __name__, static_folder='static', template_folder='templates')

from app.vehicle_registration import routes, api
