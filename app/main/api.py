from datetime import datetime, timedelta, timezone
import os
import re
import time
from flask_mail import Message
from app.constants.address import PROVINCE, BARANGAY
from app.main import main_bp as bp
from app import mail, jwt
from flask import jsonify, make_response, request, redirect, flash, session, url_for
from firebase_admin import db, storage, auth
from app import socketio
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
)
from app.main.jwt import refresh_token
from config import FirebaseConfig
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import asyncio
from app.utils import generate_faces
import bcrypt
import random
import smtplib
from email.mime.text import MIMEText
from app.utils import send_email


# Email regex pattern for validation
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
# Phone number regex pattern for validation (example pattern, adjust as needed)
PHONE_REGEX = r"^\+?1?\d{9,15}$"


def verify_laravel_hash(password, hashed_password):
    try:
        # Ensure we're using bytes
        password_bytes = password.encode("utf-8")
        hash_bytes = hashed_password.encode("utf-8")

        # Verify password using bcrypt
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        print(f"Password verification error: {str(e)}")
        return False


@bp.route("/api/login", methods=["POST"])
def login():
    admin_name = request.form["admin_name"]
    password = request.form["password"]
    admin_ref = db.reference("ADMIN_CRED")
    admin_cred = admin_ref.child(admin_name).get()

    # Check if the admin credentials exist and verify the password
    if admin_cred and verify_laravel_hash(password, admin_cred["password"]):
        access_token = create_access_token(
            identity=admin_name,
            additional_claims={
                "full_name": f"{admin_cred['first_name']} {admin_cred['last_name']}",
                "position": admin_cred["position"],
            },
        )
        # Create a response object
        response = make_response(redirect(url_for("main.dashboard")))
        set_access_cookies(response, access_token)
        # Redirect to the dashboard if login is successful
        return response
    else:
        # Flash an error message and redirect back to the login page
        flash("Invalid credentials, please try again.", "error")
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
            ]
        ):
            flash("All fields are required.")
            return redirect(url_for("main.register"))

        # Validate email format
        if not re.match(EMAIL_REGEX, email):
            flash("Invalid email format.")
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
            }
            if image:
                storage_url = FirebaseConfig.STORAGE_BUCKET
                # Upload image to Firebase Storage with the correct MIME type
                blob = storage.bucket(storage_url).blob(f"Images/{id_number}.jpg")
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

            flash("Registration successful. Redirecting to login page in 3 sec...", "success")
            asyncio.run(generate_faces())
            # add a delay before redirecting to login page
            time.sleep(3)
            return redirect(url_for("main.register"))

        except Exception as e:
            flash("Failed to register. Please try again.", "error")
            print("Failed to create student:", e)
            return redirect(url_for("main.register"))


# signout
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
    attendance_ref = db.reference(f"attendance/{course}")

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
                if "time_in" in student_data:
                    # Single entry
                    record = {
                        "date": date,
                        "time_in": student_data["time_in"],
                        "time_out": (
                            student_data["time_out"]
                            if student_data["time_out"]
                            else "Not checked out"
                        ),
                        "duration": calculate_duration(
                            student_data["time_in"], student_data["time_out"]
                        ),
                    }
                    student_records.append(record)
                else:
                    # Multiple entries
                    for entry_id, entry_data in student_data.items():
                        record = {
                            "date": date,
                            "time_in": entry_data["time_in"],
                            "time_out": (
                                entry_data["time_out"]
                                if entry_data["time_out"]
                                else "Not checked out"
                            ),
                            "duration": calculate_duration(
                                entry_data["time_in"], entry_data["time_out"]
                            ),
                        }
                        student_records.append(record)

    # Fetch student details
    students_ref = db.reference("Students")
    student_data = students_ref.child(student_id).get()

    if not student_data:
        return jsonify({"message": "Student not found"}), 404

    if student_data.get("program") != program:
        return jsonify({"message": "Student not in the specified program"}), 400

    # Prepare the response
    filtered_records = {
        student_id: {
            "name": f"{student_data.get('first_name', '')} {student_data.get('last_name', '')}",
            "records": student_records,
        }
    }

    return jsonify(filtered_records), 200


def calculate_duration(time_in, time_out):
    if not time_out:
        return "N/A"
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
    position = request.form.get("position")

    # Validate required fields
    if not all([first_name, last_name, email, password, confirm_password, position]):
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
        hashed_password = hash_password_laravel_compatible(password)

        # Store additional user information in the database
        admin_ref = db.reference("ADMIN_CRED")
        if admin_ref.child(username).get() is not None:
            flash("Username already exists. Please try again.", "error")
            return redirect(url_for("main.signup"))
        admin_ref.child(username).set(
            {
                "password": hashed_password,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "position": position,
            }
        )

        flash("Signup successful. Please log in.", "success")
        return redirect(url_for("main.login_page"))

    except Exception as e:
        flash("Failed to sign up. Please try again.", "error")
        print("Failed to create admin:", e)
        return redirect(url_for("main.signup"))


# Hash the password
def hash_password_laravel_compatible(password):
    # Ensure cost factor matches Laravel's default (10)
    salt = bcrypt.gensalt(rounds=10)
    # Encode password to bytes
    password_bytes = password.encode("utf-8")
    # Generate hash
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Replace $2b$ with $2y$ to match Laravel's format
    return hashed.decode("utf-8").replace("$2b$", "$2y$")


@bp.route("/api/create-staff", methods=["POST"])
# @jwt_required()
def create_account():
    try:
        # Get form data
        username = request.form.get("username")
        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        middle_initial = request.form.get("middleInitial")
        email = request.form.get("email")
        password = request.form.get("password")

        # Validate required fields
        if not all([username, first_name, last_name, email, password]):
            return jsonify({"error": "All required fields must be filled"}), 400

        # Validate email format
        if not re.match(EMAIL_REGEX, email):
            flash("Invalid email format.", "error")
            return redirect(url_for("main.create_staff"))

        # Check if username already exists
        staff_ref = db.reference("Staffs")
        if staff_ref.child(username).get():
            flash("Username already exists. Please choose a different username.", "error")
            return redirect(url_for("main.create_staff"))

        # Create staff data structure
        staff_data = {
            "name": username,
            "first_name": first_name,
            "last_name": last_name,
            "middle_initial": middle_initial,
            "email": email,
            "password": hash_password_laravel_compatible(password),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "email_verified_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "0",
        }

        # Create staff account
        staff_ref.child(username).set(staff_data)

        # Create activity log
        # log_ref = db.reference("ActivityLogs")
        # log_data = {
        #     "action": "create_staff",
        #     "created_at": datetime.now(timezone.utc).isoformat(),
        #     "description": f"Created new staff account for {username}",
        #     "performed_by": get_jwt_identity()
        # }
        # log_ref.push(log_data)
        send_email(username=username, password=password, recipient_email=email)
        
        flash("Staff account created successfully!", "success")

        return redirect(url_for("main.create_staff"))

    except Exception as e:
        flash("Error creating staff. Please try again.", "error")
        print(f"Error creating staff: {str(e)}")
        return redirect(url_for("main.create_staff"))


@bp.route("/api/update-profile", methods=["POST"])
def update_profile():
    try:
        # Get form data
        data = {
            "badge_number": request.form.get("badgeNumber"),
            "first_name": request.form.get("firstName"),
            "middle_name": request.form.get("middleName"),
            "last_name": request.form.get("lastName"),
            "gender": request.form.get("gender"),
            "civil_status": request.form.get("civilStatus"),
            "contact_no": request.form.get("contactNo"),
            "date_of_birth": request.form.get("dateOfBirth"),
            "province": request.form.get("province"),
            "city": request.form.get("city"),
            "barangay": request.form.get("barangay"),
            "employment_type": request.form.get("employmentType"),
            "position": request.form.get("position"),
            "emergency_contact": request.form.get("emergencyContact"),
            "emergency_contact_no": request.form.get("emergencyContactNo"),
            "date_hired": request.form.get("dateHired"),
            "schedule": request.form.get("schedule"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": request.form.get("username"),
        }

        # Validate required fields
        required_fields = ["badge_number", "first_name", "last_name", "contact_no"]
        for field in required_fields:
            if not data[field]:
                return (
                    jsonify(
                        {"error": f"{field.replace('_', ' ').title()} is required"}
                    ),
                    400,
                )
        # Update profile in database
        admin_ref = db.reference(
            f"ADMIN_CRED/{data['username']}"
        )  # Change this to the current user's username}")
        admin_ref.update(data)

        # flash('Profile updated successfully!', 'success')
        return jsonify({"message": "Profile updated successfully!"}), 200

    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        flash("Error updating profile. Please try again.", "error")
        return redirect(url_for("main.profile"))


UPLOAD_FOLDER = os.path.join("app", "static", "profile_photos")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/api/update-profile-photo", methods=["POST"])
def update_profile_photo():
    try:
        # Check if folder exists, if not create it
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        if "photo" not in request.files:
            return jsonify({"message": "No file uploaded"}), 400

        file = request.files["photo"]
        username = request.form.get("username")

        if file.filename == "":
            return jsonify({"message": "No file selected"}), 400

        if file and allowed_file(file.filename):
            # Save file with username as filename
            filename = f"{username}.jpg"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            return jsonify(
                {
                    "status": "success",
                    "message": "Profile photo updated successfully",
                    "photo_url": url_for(
                        "static", filename=f"profile_photos/{filename}"
                    ),
                }
            )

        return jsonify({"message": "Invalid file type"}), 400

    except Exception as e:
        print(f"Upload error: {str(e)}")  # For debugging
        return jsonify({"message": "Server error occurred"}), 500


@bp.route("/api/forgot-password", methods=["POST"])
def handle_forgot_password():
    email = request.form.get("email")
    if not email:
        return jsonify({"message": "Email is required."}), 400

    # Check if email exists in the database
    admin_ref = db.reference("ADMIN_CRED")
    admin_data = admin_ref.order_by_child("email").equal_to(email).get()

    if admin_data:
        admin_key = list(admin_data.keys())[0]
        admin = admin_data[admin_key]
        current_time = int(time.time())

        # Check if there's an unexpired OTP
        if "otp_expiry" in admin and admin["otp_expiry"] > current_time:
            return (
                jsonify(
                    {
                        "message": "An OTP has already been sent. Please wait before requesting a new one."
                    }
                ),
                429,
            )

        # Generate and send new OTP
        otp = generate_otp()
        send_otp_email(email, otp)
        admin_ref.child(admin_key).update(
            {"otp": otp, "otp_expiry": current_time + 300}  # 5 minutes expiry
        )

    session["verified_email"] = email
    return jsonify({"message": "OTP sent to your email."}), 200


def generate_otp():
    return str(random.randint(100000, 999999))  # Generate a 6-digit OTP


def send_otp_email(email, otp):
    # Email configuration
    sender_email = "secureu07@gmail.com"  # Replace with your email
    sender_password = "uqwo qgoh sjlr zucs"  # Replace with your password
    subject = "Your OTP Code"
    body = f"Your OTP code is: {otp}"

    # Create the email
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = email

    try:
        # Send the email
        with smtplib.SMTP(
            "smtp.gmail.com", 587
        ) as server:  # Update SMTP server if needed
            server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("OTP sent successfully to:", email)
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
    except Exception as e:
        print(f"Failed to send OTP: {e}")


@bp.route("/api/verify-otp", methods=["POST"])
def verify_otp():
    email = session.get("verified_email")
    otp = request.form.get("otp")

    if not email or not otp:
        return jsonify({"message": "Email and OTP are required."}), 400

    # Get admin record
    admin_ref = db.reference("ADMIN_CRED")
    admin_data = admin_ref.order_by_child("email").equal_to(email).get()

    if not admin_data:
        return jsonify({"message": "Invalid email."}), 404

    admin_key = list(admin_data.keys())[0]
    admin = admin_data[admin_key]

    # Verify OTP
    current_time = int(time.time())
    if (
        "otp" not in admin
        or admin["otp"] != otp
        or "otp_expiry" not in admin
        or admin["otp_expiry"] < current_time
    ):
        return jsonify({"message": "Invalid or expired OTP."}), 400

    session["verified_email"] = email

    # Clear OTP after successful verification
    admin_ref.child(admin_key).update({"otp": None, "otp_expiry": None})

    return jsonify({"message": "OTP verified successfully."}), 200


@bp.route("/api/reset-password", methods=["POST"])
def reset_password():
    email = session.get("verified_email")
    new_password = request.form.get("password")

    if not email or not new_password:
        return jsonify({"message": "All fields are required."}), 400

    # Get admin record
    admin_ref = db.reference("ADMIN_CRED")
    admin_data = admin_ref.order_by_child("email").equal_to(email).get()

    if not admin_data:
        return jsonify({"message": "Invalid email."}), 404

    admin_key = list(admin_data.keys())[0]
    # admin = admin_data[admin_key]

    # Update password
    admin_ref.child(admin_key).update(
        {"password": hash_password_laravel_compatible(new_password)}
    )

    return jsonify({"message": "Password updated successfully."}), 200


@bp.route("/api/add-to-archive", methods=["POST"])
def add_to_archive():
    student_id = request.form.get("student_id")
    if not student_id:
        return jsonify({"message": "Student ID is required."}), 400

    # Get student record
    student_ref = db.reference("Students")
    student_data = student_ref.child(student_id).get()

    if not student_data:
        return jsonify({"message": "Student not found."}), 404

    student_ref.child(student_id).update({"archived": True})

    return jsonify({"message": "Student added to archive."}), 200


@bp.route("/api/remove-from-archive", methods=["POST"])
def remove_from_archive():
    student_id = request.form.get("student_id")
    if not student_id:
        return jsonify({"message": "Student ID is required."}), 400

    # Get student record
    student_ref = db.reference("Students")
    student_ref.child(student_id).update({"archived": False})

    return jsonify({"message": "Student removed from archive."}), 200


@bp.route("/api/remove-student-permanently", methods=["POST"])
def remove_student_permanently():
    student_id = request.form.get("student_id")
    if not student_id:
        return jsonify({"message": "Student ID is required."}), 400

    # Get student record
    student_ref = db.reference("Students")
    student_data = student_ref.child(student_id).get()

    if not student_data:
        return jsonify({"message": "Student not found."}), 404

    student_ref.child(student_id).delete()

    return jsonify({"message": "Student removed permanently."}), 200

@bp.route("/api/add-employee", methods=["POST"])
def add_employee():
    try:
        employee_id = request.form.get("employeeid")
        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        middle_initial = request.form.get("middleInitial")
        designation = request.form.get("designation")
        department = request.form.get("department")
        emp_type = request.form.get("empType")
        emp_image = request.files.get("empImage")

        # Validate required fields
        if not all([employee_id, first_name, last_name, designation, department, emp_type]):
            flash("All fields are required.", category="error")
            return redirect(url_for("main.employees"))

        # Create employee data structure
        employee_data = {
            "employee_id": employee_id,
            "first_name": first_name,
            "last_name": last_name,
            "middle_initial": middle_initial,
            "designation": designation,
            "department": department,
            "emp_type": emp_type,
        }

        if emp_image:
            storage_url = FirebaseConfig.STORAGE_BUCKET
            # Upload image to Firebase Storage with the correct MIME type
            blob = storage.bucket(storage_url).blob(f"EmployeeImages/{employee_id}.jpg")
            blob.upload_from_file(emp_image, content_type="image/jpeg")
            blob.make_public()
            image_url = blob.public_url
            employee_data["image_url"] = image_url

        # Save employee data to the database
        employee_ref = db.reference("Employees")
        employee_ref.child(employee_id).set(employee_data)

        flash("Employee added successfully!", category="success")
        return redirect(url_for("main.employees"))

    except Exception as e:
        print(f"Error adding employee: {str(e)}")
        return jsonify({"error": "Failed to add employee. Please try again."}), 500
    
    
@bp.route("/api/update-employee", methods=["POST"])
def update_employee():
    try:
        employee_id = request.form.get("employeeid")
        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        middle_initial = request.form.get("middleInitial")
        designation = request.form.get("designation")
        department = request.form.get("department")
        emp_type = request.form.get("empType")
        emp_image = request.files.get("empImage")

        # Validate required fields
        if not all([employee_id, first_name, last_name, designation, department, emp_type]):
            flash("All fields are required.", category="error")
            return redirect(url_for("main.employees"))

        # Create employee data structure
        employee_data = {
            "first_name": first_name,
            "last_name": last_name,
            "middle_initial": middle_initial,
            "designation": designation,
            "department": department,
            "emp_type": emp_type,
        }

        if emp_image:
            storage_url = FirebaseConfig.STORAGE_BUCKET
            # Upload image to Firebase Storage with the correct MIME type
            blob = storage.bucket(storage_url).blob(f"EmployeeImages/{employee_id}.jpg")
            blob.upload_from_file(emp_image, content_type="image/jpeg")
            
            # Generate a signed URL for the image
            expiration_time = timedelta(days=365*100)  # URL valid for 100 years
            image_url = blob.generate_signed_url(expiration=expiration_time)
            employee_data["image_url"] = image_url

        # Update employee data in the database
        employee_ref = db.reference("Employees")
        employee_ref.child(employee_id).update(employee_data)

        flash("Employee updated successfully!", category="success")
        return redirect(url_for("main.employees"))

    except Exception as e:
        print(f"Error updating employee: {str(e)}")
        return jsonify({"error": "Failed to update employee. Please try again."}), 500