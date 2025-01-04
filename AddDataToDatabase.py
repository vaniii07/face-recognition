import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from config import FirebaseConfig
# Ensure the path to your service account key JSON file is correct
cred = credentials.Certificate(r"serviceAccountKey.json")

# Correctly specify the database URL
database_url = FirebaseConfig.DATABASE_URL

# Initialize the Firebase app with the correct database URL
firebase_admin.initialize_app(cred, {
    'databaseURL': database_url  # Ensure 'databaseURL' key is correctly specified
})

# Debug: Print the database URL to ensure it's correct
print(f"Database URL: {database_url}")

# Reference to the 'Students' node in the database
ref = db.reference('Students')

# Sample data to be added
data = {
    "20214040": {
        "last_entered_time": "2024-5-29 00:54:34",
        "name": "David Earl Gabriel Garcia",
        "course": "BSIT",
        "total_entered": 0,
        "gender": "Male",
        "time_in": "8am",
        "time_out": "5pm",
        "year": 3,
        "phone_number": "+639569473576"
    },
    "20215428": {
        "last_entered_time": "2024-5-29 00:54:34",
        "name": "Ivan Sison",
        "course": "BSIT",
        "total_entered": 0,
        "gender": "Male",
        "time_in": "8am",
        "time_out": "5pm",
        "year": 3,
        "phone_number": "+639930736712"
    },
    "20214715": {
        "last_entered_time": "2024-5-29 00:54:34",
        "name": "Austin Angelo Aquino",
        "course": "BSIT",
        "total_entered": 0,
        "time_in": "8am",
        "gender": "Male",
        "time_out": "5pm",
        "year": 3,
        "phone_number": "+639383484029"
    },
    "20217336": {
        "last_entered_time": "2024-5-29 00:54:34",
        "name": "Raymark Mina",
        "course": "BSIT",
        "total_entered": 0,
        "time_in": "8am",
        "gender": "Male",
        "time_out": "5pm",
        "year": 3,
        "phone_number": "+639480150374"
    },
    "20215710": {
        "last_entered_time": "2024-5-29 00:54:34",
        "name": "Angelo Gabertan",
        "course": "BSIT",
        "total_entered": 0,
        "time_in": "8am",
        "gender": "Male",
        "time_out": "5pm",
        "year": 3,
        "phone_number": "+639673215147"
    },
    "20212809": {
            "last_entered_time": "2024-5-29 00:54:34",
            "name": "Lea Mae Cruz",
            "course": "BSIT",
            "total_entered": 0,
            "time_in": "8am",
            "gender": "Female",
            "time_out": "5pm",
            "year": 3,
            "phone_number": "+639673215147"
    }
}

# Adding data to the database
for key, value in data.items():
    ref.child(key).set(value)
    print(f"Data for {key} set successfully")
