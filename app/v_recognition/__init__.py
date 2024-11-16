from flask import Blueprint

bp_v_recognition = Blueprint('v_recognition', __name__)

from app.v_recognition import routes
