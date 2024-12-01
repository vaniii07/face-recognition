from flask import json, render_template, request, redirect, flash, url_for, jsonify
from app.main import main_bp as bp
from app.constants.address import PROVINCE, BARANGAY
from app.constants.courses import COURSES, COURSE_MAPPING, PROGRAM_MAPPING
from datetime import datetime
from firebase_admin import db
from app import socketio
from app.main.jwt import refresh_token
from flask_jwt_extended import get_jwt, get_jwt_identity
import os
from werkzeug.utils import secure_filename

active_listeners = {
    "attendance": {},
    "monitoring": None,
    "monthly_attendance": None,
    "students": {},   
}


@bp.route("/")
def login_page():
    return render_template("login.html")

@bp.route("/dashboard")
@refresh_token()
def dashboard():
    def listen_to_attendance(courses):
        current_date = datetime.now().strftime("%Y-%m-%d")

        def attendance_listener(event, course):
            # Fetch the entire data from the reference
            attendance_data = db.reference(f"attendance/{course}/{current_date}").get()
            if attendance_data:
                # Count the number of students
                count = len(attendance_data)
                # Emit the entire data to the client
                socketio.emit(
                    "update_data",
                    {"course": course, "data": attendance_data, "count": count},
                )

        # Set up listeners for each course
        for course in courses:
            attendance_ref = db.reference(f"attendance/{course}/{current_date}")
            # Check if the reference exists and if the listener is already active
            if attendance_ref.get() is not None and course not in active_listeners["attendance"]:
                listener = attendance_ref.listen(
                    lambda event, course=course: attendance_listener(event, course)
                )
                active_listeners["attendance"][course] = listener
            else:
                print(f"Listener for course {course} is already active or reference does not exist.")

    current_date = datetime.now().strftime("%Y-%m-%d")

    def listen_to_monitoring():
        def monitoring_listener(event):
            monitoring_data = (
                db.reference(f"monitoring").order_by_key().start_at(current_date).get()
            )
            socketio.emit("update_monitoring", monitoring_data)

        monitoring_ref = db.reference("monitoring")
        # Check if the listener is already active
        if active_listeners["monitoring"] is None:
            listener = monitoring_ref.listen(monitoring_listener)
            active_listeners["monitoring"] = listener
        else:
            print("Monitoring listener is already active.")

    def listen_to_monthly_attendance():
        def monthly_attendance_listener(event):
            attendance_data = db.reference("attendance").get()
            initial_monthly_attendance_data = {}

            if attendance_data:
                for first_level_value in attendance_data.values():
                    for date_key, date_value in first_level_value.items():
                        if date_key not in initial_monthly_attendance_data:
                            initial_monthly_attendance_data[date_key] = {}
                        initial_monthly_attendance_data[date_key].update(date_value)

            socketio.emit("update_monthly_attendance", initial_monthly_attendance_data)

        attendance_ref = db.reference("attendance")
        # Check if the listener is already active
        if active_listeners["monthly_attendance"] is None:
            listener = attendance_ref.listen(monthly_attendance_listener)
            active_listeners["monthly_attendance"] = listener
        else:
            print("Monthly attendance listener is already active.")

    # Example call to the function with an array of courses
    courses = COURSES

    listen_to_attendance(courses)
    listen_to_monitoring()
    listen_to_monthly_attendance()

    # Fetch initial data for each course
    current_date = datetime.now().strftime("%Y-%m-%d")
    initial_data = {}
    for course in courses:
        attendance_ref = db.reference(f"attendance/{course}/{current_date}")
        data = attendance_ref.get()
        count = len(data) if data else 0
        initial_data[course] = {"data": data, "count": count}

    # Fetch initial monitoring data
    monitoring_ref = db.reference(f"monitoring")
    query = monitoring_ref.order_by_key().start_at(current_date)
    initial_monitoring_data = query.get()

    # Fetch initial monthly attendance data
    attendance_ref = db.reference("attendance")
    attendance_data = attendance_ref.get()

    initial_monthly_attendance_data = {}

    if attendance_data:
        for first_level_value in attendance_data.values():
            for date_key, date_value in first_level_value.items():
                if date_key not in initial_monthly_attendance_data:
                    initial_monthly_attendance_data[date_key] = {}
                for student_id, attendance_info in date_value.items():
                    student_ref = db.reference(f"Students/{student_id}")
                    student_info = student_ref.get()
                    if student_info:
                        attendance_info["student_name"] = f"{student_info.get('first_name', '')} {student_info.get('last_name', '')}"
                    initial_monthly_attendance_data[date_key][student_id] = attendance_info

    return render_template(
        "dashboard.html",
        programs=PROGRAM_MAPPING,
        courses=COURSE_MAPPING,
        initial_data=initial_data,
        initial_monitoring_data=initial_monitoring_data,
        initial_monthly_attendance_data=initial_monthly_attendance_data,
    )


@bp.route("/register")
def register():
    return render_template(
        "registration_form.html",
        provinces=PROVINCE,
        barangays=BARANGAY,
        courses=COURSE_MAPPING,
        course_with_program=COURSES,
    )
@bp.route("/students/<course>", defaults={"program": None})
@bp.route("/students/<course>/<program>")
@refresh_token()
def students(course, program):
    student_ref = db.reference("Students")
    monitoring_ref = db.reference("monitoring")

    # Fetch initial data
    students_by_course = student_ref.order_by_child("course").equal_to(course).get()

    # Filter by program if program is provided
    if program:
        student_list = [
            {**student, "id": key}
            for key, student in students_by_course.items()
            if student.get("program") == program
            and not student.get("archived", False)
        ]
    else:
        student_list = [
            {**student, "id": key} for key, student in students_by_course.items()
        ]

        # Get attendance history
    attendance_history = get_attendance_history(student_list, monitoring_ref, program)
    
    # Get today's count for each student
    today_count = get_today_count(student_list, monitoring_ref)
    exit_count = get_exit_count(student_list, monitoring_ref)

    # Attach today_count to each student in the student_list
    for student in student_list:
        student_id = student["id"]
        student["today_count"] = today_count.get(student_id, 0)
        student["exit_count"] = exit_count.get(student_id, 0)

    # Function to listen to changes in the "Students" reference
    def student_listener(event):
        updated_students = student_ref.get()
        updated_student_list = [
            {**student, "id": key}
            for key, student in updated_students.items()
            if student["course"] == course
        ]
        
        # Attach today_count to each student in the updated_student_list
        today_count = get_today_count(updated_student_list, monitoring_ref)
        exit_count = get_exit_count(updated_student_list, monitoring_ref)
        for student in updated_student_list:
            student_id = student["id"]
            student["today_count"] = today_count.get(student_id, 0)
            student["exit_count"] = exit_count.get(student_id, 0)

        socketio.emit(f"update_{course}_students", updated_student_list)

    # Set up the listener if not already active
    if course not in active_listeners["students"]:
        listener = student_ref.listen(student_listener)
        active_listeners["students"][course] = listener
    else:
        print(f"Listener for course {course} is already active.")

    if program:
        course_name = f"{COURSE_MAPPING[course]} - {PROGRAM_MAPPING[program]}"
    else:
        course_name = COURSE_MAPPING[course]
        
    claims = get_jwt()
    
    current_user = {
        "full_name": claims["full_name"],
        "position": claims["position"]
    }
    

    return render_template(
        "index.html",
        initial_data=student_list,
        course=course,
        course_name=course_name,
        course_mapping=COURSE_MAPPING,
        attendance_history=attendance_history,
        current_user=current_user
    )

def get_today_count(student_list, monitoring_ref):
    current_date = datetime.now().strftime("%Y-%m-%d")
    today_count = {}
    for student in student_list:
        student_id = student["id"]
        # Query monitoring data for the specific student_id
        student_monitoring_data = monitoring_ref.order_by_child("student_id").equal_to(student_id).get()
        count = sum(1 for key, data in student_monitoring_data.items() if data["updated_time"].startswith(current_date) and data["attendance_type"] == "entered")        
        today_count[student_id] = count
    return today_count

def get_exit_count(student_list, monitoring_ref):
    current_date = datetime.now().strftime("%Y-%m-%d")
    today_count = {}
    for student in student_list:
        student_id = student["id"]
        # Query monitoring data for the specific student_id
        student_monitoring_data = monitoring_ref.order_by_child("student_id").equal_to(student_id).get()
        count = sum(1 for key, data in student_monitoring_data.items() if data["updated_time"].startswith(current_date) and data["attendance_type"] == "exited")        
        today_count[student_id] = count
    return today_count

def get_attendance_history(student_list, monitoring_ref, program):
    attendance_history = {}
    for student in student_list:
        student_id = student["id"]
        # Query monitoring data for the specific student_id
        student_monitoring_data = monitoring_ref.order_by_child("student_id").equal_to(student_id).get()
        for key, data in student_monitoring_data.items():
            if not program or data["program"] == program:
                date_key = data["updated_time"].split(" ")[0]
                if date_key not in attendance_history:
                    attendance_history[date_key] = {
                        "students": {},
                        "today_count": 0,  # Will be recalculated for each date
                        "exit_count": 0    # Will be recalculated for each date
                    }
                
                if student_id not in attendance_history[date_key]["students"]:
                    attendance_history[date_key]["students"][student_id] = {
                        "student": student,
                        "attendance_data": []
                    }
                
                attendance_history[date_key]["students"][student_id]["attendance_data"].append(data)

    # Recalculate counts for each date after all data is collected
    for date_key in attendance_history:
        today_count = 0
        exit_count = 0
        # Count unique students who entered and exited for this date
        entered_students = set()
        exited_students = set()
        
        for student_id, student_data in attendance_history[date_key]["students"].items():
            for record in student_data["attendance_data"]:
                if record["attendance_type"] == "entered":
                    entered_students.add(student_id)
                elif record["attendance_type"] == "exited":
                    exited_students.add(student_id)
        
        attendance_history[date_key]["today_count"] = len(entered_students)
        attendance_history[date_key]["exit_count"] = len(exited_students)

    print(attendance_history)
    # Convert the dictionary to the desired format
    formatted_attendance_history = {}
    for date_key, record in attendance_history.items():
        formatted_attendance_history[date_key] = []
        for student_id, student_record in record["students"].items():
            formatted_attendance_history[date_key].append({
                "student": student_record["student"],
                "attendance_data": student_record["attendance_data"],
                "today_count": record["today_count"],
                "exit_count": record["exit_count"]
            })
    
    return formatted_attendance_history
    
# @bp.route("/students/<course>", defaults={"program": None})
# @bp.route("/students/<course>/<program>")
# @refresh_token()
# def students_test(course, program):
#     # Return empty list for initial data
#     student_list = []

#     # No Firebase listener needed for testing

#     if program:
#         course_name = f"{COURSE_MAPPING[course]} - {PROGRAM_MAPPING[program]}"
#     else:
#         course_name = COURSE_MAPPING[course]

#     return render_template(
#         "index.html",
#         initial_data=student_list,
#         course=course,
#         course_name=course_name,
#         course_mapping=COURSE_MAPPING,
#     )


@bp.route("/viewing")
@refresh_token()
def viewing():
    current_date = datetime.now().strftime("%Y-%m-%d")
    # Fetch initial monitoring data
    monitoring_ref = db.reference(f"monitoring")
    query = monitoring_ref.order_by_key().start_at(current_date).limit_to_last(8)
    initial_monitoring_data = query.get()

    # Define a callback function to handle data changes
    def listener(event):
        # Fetch the latest data
        updated_data = query.get()
        # Reverse the order to get the latest entries first
        if updated_data:
            sorted_updated_data = dict(reversed(list(updated_data.items())))
        else:
            sorted_updated_data = {}
        # Emit the updated data to the client
        socketio.emit("update_viewing", sorted_updated_data)

    # Attach the listener to the Firebase reference
    if monitoring_ref not in active_listeners:
        active_listeners["monitoring_ref"] = monitoring_ref
    monitoring_ref.listen(listener)

    return render_template(
        "viewing.html",
        initial_monitoring_data=initial_monitoring_data,
        programs=PROGRAM_MAPPING,
        courses=COURSE_MAPPING,
    )

@bp.route("/profile")
@refresh_token()
def profile():
    current_user = get_jwt_identity()
    admin_ref = db.reference("ADMIN_CRED")
    admin_data = admin_ref.child(current_user).get()
    
    if admin_data:
        return render_template("profile.html", admin_data=admin_data, username=current_user)
    

@bp.route("/signup")
def signup():
    return render_template("signup.html")

@bp.route("/activity-logs")
@refresh_token()
def activity_logs():
    activity_logs_ref = db.reference("ActivityLogs")
    activity_logs = activity_logs_ref.get()
    print(activity_logs)
    if activity_logs is None:
        activity_logs = []
    return render_template("logs.html", activity_logs=activity_logs)

@bp.route("/create-staff")
@refresh_token()
def create_staff():
    return render_template("create_staff.html")

@bp.route("/staffs")
@refresh_token()
def staffs():
    staff_ref = db.reference("Staffs")
    staffs_data = staff_ref.get()
    print(staffs_data)
    if staffs_data is None:
        staffs_data = []
        
    return render_template("staffs.html", staffs=staffs_data)

@bp.route('/forgot-password')
def forgot_password():
    return render_template('forgotpass.html')

@bp.route('/archived')
@refresh_token()
def archived():
    # Get reference to main Students node
    student_ref = db.reference("Students")
    
    # Query for archived students
    archived_students = {}
    all_students = student_ref.get()
    
    if all_students:
        # Filter students where archived=True
        archived_students = {
            k: v for k, v in all_students.items() 
            if v.get('archived', False) == True
        }
    
    return render_template("archived.html", students=archived_students)

