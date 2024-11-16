from firebase_admin import credentials, exceptions, initialize_app, get_app
from config import FirebaseConfig

firebase_app = None

def initialize_firebase():
    global firebase_app
    cred = credentials.Certificate(FirebaseConfig.CRED)
    try:
        firebase_app = initialize_app(cred, {
            'databaseURL': FirebaseConfig.DATABASE_URL,
            'storageBucket': FirebaseConfig.STORAGE_BUCKET
        })
    except exceptions.FirebaseError as firebase_error:
        # Log the error instead of printing
        print(f"Firebase Initialization Error: {firebase_error}")
    return firebase_app

def get_firebase_app():
    global firebase_app
    if not firebase_app:
        firebase_app = get_app()
    return firebase_app