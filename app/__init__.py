from datetime import timedelta
from flask_socketio import SocketIO
from flask import Flask
from config import Config, FirebaseConfig
from flask_mail import Mail, Message
from flask_jwt_extended import JWTManager
from config import Config
app = Flask(__name__)
socketio = SocketIO(app)
app.config.from_object(Config)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = Config.GMAIL_EMAIL
app.config['MAIL_PASSWORD'] = Config.GMAIL_APP_PASSWORD
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)
app.secret_key = Config.SECRET_KEY
app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_CSRF_IN_COOKIES'] = True
app.config['JWT_CSRF_COOKIE_EXPIRES'] = timedelta(days=1)  # Set CSRF token expiry to 1 hour
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)  # Set access token expiry to 1 hour

jwt = JWTManager(app)
from app import error_handler
from firebase import initialize_firebase
initialize_firebase()
from app.main import main_bp
from app.v_recognition import bp_v_recognition
from app.vehicle_registration import vehicle_registration_bp
app.register_blueprint(main_bp)
app.register_blueprint(bp_v_recognition)
app.register_blueprint(vehicle_registration_bp, url_prefix='/vehicle')

