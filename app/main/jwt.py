from datetime import datetime, timezone, timedelta
from flask import make_response
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required, set_access_cookies, verify_jwt_in_request
from functools import wraps
import pytz
from werkzeug.exceptions import Unauthorized

def refresh_access(response):
    jwt_data = get_jwt()
    exp_timestamp = jwt_data["exp"]
    manila_tz = pytz.timezone('Asia/Manila')
    now_manila = datetime.now(manila_tz)
    now = now_manila.timestamp()
    target_timestamp = timedelta(hours=12).total_seconds()

    if exp_timestamp - now < target_timestamp:
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        set_access_cookies(response, access_token)
    return response

def refresh_token():
    def wrapper(fn):
        @wraps(fn)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
            except Exception as e:
                raise Unauthorized("Missing or invalid token")
            response = make_response()
            response = refresh_access(response)
            original_response = fn(*args, **kwargs)
            response.data = original_response
            return response
        return decorated_function
    return wrapper

