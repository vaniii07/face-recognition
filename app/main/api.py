from datetime import datetime, timedelta, timezone
import re
import time
from flask_mail import Message
from app.constants.address import PROVINCE, BARANGAY
from app.main import main_bp as bp
from app import mail, jwt
from flask import jsonify, make_response, request, redirect, flash, session, url_for
from firebase_admin import db, storage, auth
from app import socketio
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from app.main.jwt import refresh_token
from config import FirebaseConfig
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import asyncio
from app.utils import generate_faces

# Email regex pattern for validation
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
# Phone number regex pattern for validation (example pattern, adjust as needed)
PHONE_REGEX = r"^\+?1?\d{9,15}$"

@bp.route("/api/login", methods=["POST"])
def login():
    admin_name = request.form["admin_name"]
    password = request.form["password"]
    admin_ref = db.reference("ADMIN_CRED")
    admin_cred = admin_ref.child(admin_name).get()

    # Check if the admin credentials exist and verify the password
    if admin_cred and check_password_hash(admin_cred.get("password"), password):
        access_token = create_access_token(identity=admin_name)
        # Create a response object
        response = make_response(redirect(url_for("main.dashboard")))
        set_access_cookies(response, access_token)
        # Redirect to the dashboard if login is successful
        return response
    else:
        # Flash an error message and redirect back to the login page
        flash("Invalid credentials, please try again.")
        return redirect(url_for("main.login_page"))

@bp.route("/api/submit", methods=["POST"])
def submit():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        middle_initial = request.form.get("middle_initial")
        last_name = request.form.get("last_name")
        day = request.form.get("day")
        month = request.form.get("month")
        year = request.form.get("year")
        phone = request.form.get("phone")
        province = request.form.get("province")
        city = request.form.get("city")
        barangay = request.form.get("barangay")
        address = request.form.get("address")
        zip_code = request.form.get("zip_code")
        email = request.form.get("email")
        id_number = request.form.get("id_number")
        school_year = request.form.get("school_year")
        image = request.files.get("image")
        course = request.form.get("course")
        program = request.form.get("program")
        gender = request.form.get("gender")
        guardian_parent_email = request.form.get("guardian_parent_email")

        errors = []
        # Validate required fields
        if not all(
            [
                first_name,
                last_name,
                day,
                month,
                year,
                phone,
                province,
                address,
                zip_code,
                email,
                id_number,
                school_year,
                course,
                gender,
                guardian_parent_email,
            ]
        ):
            flash("All fields are required.")
            return redirect(url_for("main.register"))

        # Validate email format
        if not re.match(EMAIL_REGEX, email):
            flash("Invalid email format.")
            return redirect(url_for("main.register"))
        
        if not re.match(EMAIL_REGEX, guardian_parent_email):
            flash("Invalid guardian/parent email format.")
            return redirect(url_for("main.register"))

        # Validate phone number format
        if not re.match(PHONE_REGEX, phone):
            flash("Invalid phone number format.")
            return redirect(url_for("main.register"))

        try:
            user_ref = db.reference("Students")
            course_ref = db.reference("Courses")
            # Use the id_number as the key for the user
            user_data = {
                "first_name": first_name,
                "middle_initial": middle_initial,
                "last_name": last_name,
                "date_of_birth": f"{day}-{month}-{year}",
                "phone": phone,
                "province": province,
                "city": city,
                "barangay": barangay,
                "address": address,
                "zip_code": zip_code,
                "email": email,
                "id_number": id_number,
                "school_year": school_year,
                "course": course,
                "program": program,
                "gender": gender,
                "guardian_parent_email": guardian_parent_email,
            }
            if image:
                storage_url = FirebaseConfig.STORAGE_BUCKET
                # Upload image to Firebase Storage with the correct MIME type
                blob = storage.bucket(storage_url).blob(
                    f"Images/{id_number}.jpg"
                )
                blob.upload_from_file(image, content_type="image/jpeg")
                blob.make_public()
                image_url = blob.public_url
                user_data["image_url"] = image_url

            user_ref.child(id_number).set(user_data)

            # msg = Message('Registration Confirmation',
            #               sender='ivansison92@example.com',
            #               recipients=[email])
            # msg.body = f"Dear {first_name},\n\nThank you for registering.\n\nBest regards,\nYour Team"
            # mail.send(msg)
            # print('Email sent successfully')

            flash("Registration successful. Redirecting to login page in 3 sec...")
            asyncio.run(generate_faces())
            # add a delay before redirecting to login page
            time.sleep(3)
            return redirect(url_for("main.register"))

        except Exception as e:
            flash("Failed to register. Please try again.")
            print("Failed to create student:", e)
            return redirect(url_for("main.register"))

#signout
@bp.route("/api/signout", methods=["POST"])
def signout():
    response = redirect(url_for("main.login_page"))
    unset_jwt_cookies(response)
    session.clear()
    return response

def create_new_user(email, password):
    user = auth.create_user(email=email, password=password)
    print(f"Successfully created user: {user}")
    if user:
        return True
    else:
        return False

@bp.route("/api/time-records/<course>/<program>/<student_id>", methods=["GET"])
def time_records(course, program, student_id):
    # Get the reference to the attendance data for the specified course
    attendance_ref = db.reference(f'attendance/{course}')
    
    # Get all attendance data for the course
    attendance_data = attendance_ref.get()

    if not attendance_data:
        return jsonify({"message": "No attendance data found for this course"}), 404

    # Initialize a list to store processed student records
    student_records = []

    # Process the attendance data for the specific student
    for date, date_data in attendance_data.items():
        if student_id in date_data:
            student_data = date_data[student_id]
            
            # Handle both single entry and multiple entries per day
            if isinstance(student_data, dict):
                if 'time_in' in student_data:
                    # Single entry
                    record = {
                        'date': date,
                        'time_in': student_data['time_in'],
                        'time_out': student_data['time_out'] if student_data['time_out'] else 'Not checked out',
                        'duration': calculate_duration(student_data['time_in'], student_data['time_out'])
                    }
                    student_records.append(record)
                else:
                    # Multiple entries
                    for entry_id, entry_data in student_data.items():
                        record = {
                            'date': date,
                            'time_in': entry_data['time_in'],
                            'time_out': entry_data['time_out'] if entry_data['time_out'] else 'Not checked out',
                            'duration': calculate_duration(entry_data['time_in'], entry_data['time_out'])
                        }
                        student_records.append(record)

    # Fetch student details
    students_ref = db.reference('Students')
    student_data = students_ref.child(student_id).get()

    if not student_data:
        return jsonify({"message": "Student not found"}), 404

    if student_data.get('program') != program:
        return jsonify({"message": "Student not in the specified program"}), 400

    # Prepare the response
    filtered_records = {
        student_id: {
            'name': f"{student_data.get('first_name', '')} {student_data.get('last_name', '')}",
            'records': student_records
        }
    }

    return jsonify(filtered_records), 200

def calculate_duration(time_in, time_out):
    if not time_out:
        return 'N/A'
    time_in = datetime.strptime(time_in, "%H:%M:%S")
    time_out = datetime.strptime(time_out, "%H:%M:%S")
    duration = time_out - time_in
    return str(duration)


@bp.route("/api/signup", methods=["POST"])
def api_signup():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    username = request.form.get("username")

    # Validate required fields
    if not all([first_name, last_name, email, password, confirm_password]):
        flash("All fields are required.")
        return redirect(url_for("main.signup"))

    # Validate email format
    if not re.match(EMAIL_REGEX, email):
        flash("Invalid email format.")
        return redirect(url_for("main.signup"))

    if len(password) < 8:
        flash("Password must be at least 8 characters long.")
        return redirect(url_for("main.signup"))

    # Validate password match
    if password != confirm_password:
        flash("Passwords do not match.")
        return redirect(url_for("main.signup"))

    try:
        # Hash the password
        hashed_password = generate_password_hash(password)

        # Store additional user information in the database
        admin_ref = db.reference("ADMIN_CRED")
        if admin_ref.child(username).get() is not None:
            flash("Username already exists. Please try again.")
            return redirect(url_for("main.signup"))
        admin_ref.child(username).set({
            "password": hashed_password,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        })

        flash("Signup successful. Please log in.")
        return redirect(url_for("main.login_page"))

    except Exception as e:
        flash("Failed to sign up. Please try again.")
        print("Failed to create admin:", e)
        return redirect(url_for("main.signup"))
    