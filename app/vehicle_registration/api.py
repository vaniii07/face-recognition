from datetime import datetime
from flask import flash, jsonify, redirect, render_template, request, url_for
from app.vehicle_registration import vehicle_registration_bp as bp
from firebase_admin import db, storage
from config import FirebaseConfig

@bp.route("/api/verify-id", methods=["POST"])
def verify_id():
    user_id = request.form.get("studentNumber")
    
    # Check in Students reference
    studentRef = db.reference("Students")
    student = studentRef.child(user_id).get()
    
    if student:
        return redirect(url_for("vehicle_registration.register_form", user_id=user_id))
    
    # Check in Employees reference
    employeeRef = db.reference("Employees")
    employee = employeeRef.child(user_id).get()
    
    if employee:
        return redirect(url_for("vehicle_registration.register_form", user_id=user_id))
    
    # If not found in both references
    error = "User not found"
    return render_template("verify_vehicle.html", error=error)


@bp.route("/api/submit-registration", methods=["POST"])
def submit_registration():
    type = request.form.get("type")
    student_id = request.form.get("studentId")
    contact_no = request.form.get("contactNo")
    drivers_license = request.form.get("driversLicense")
    day_issued = request.form.get("daySelectIssued")
    month_issued = request.form.get("monthSelectIssued")
    year_issued = request.form.get("yearSelectIssued")
    day_expiry = request.form.get("daySelectExpiry")
    month_expiry = request.form.get("monthSelectExpiry")
    year_expiry = request.form.get("yearSelectExpiry")
    vehicle_type = request.form.get("vehicleType")
    vehicle_make = request.form.get("vehicleMake")
    vehicle_model = request.form.get("vehicleModel")
    vehicle_year = request.form.get("vehicleYear")
    plate_number = request.form.get("plateNumber")
    color = request.form.get("color")
    certificate = request.form.get("certificate")
    day_cert_issued = request.form.get("daySelectCertIssued")
    month_cert_issued = request.form.get("monthSelectCertIssued")
    year_cert_issued = request.form.get("yearSelectCertIssued")
    receipt = request.form.get("Receipt")
    day_receipt_issued = request.form.get("daySelectReceiptIssued")
    month_receipt_issued = request.form.get("monthSelectReceiptIssued")
    year_receipt_issued = request.form.get("yearSelectReceiptIssued")
    driver_name = request.form.get("driverName")
    license_number = request.form.get("licenseNumber")
    date_issued = request.form.get("dateIssued")
    expiry_date = request.form.get("expiryDate")
    relationship = request.form.get("relationship")
    vehicle_orcr = request.files.get("vehicleOrcr")
    license_card = request.files.get("licenseCard")
    vehicle_photo = request.files.get("vehiclePhoto")
    
    #If not pdf or image
    if vehicle_orcr and vehicle_orcr.filename.split('.')[-1] not in ["pdf", "png", "jpg", "jpeg"]:
        flash("Invalid file format for OR/CR", category="error")
        return render_template("verify_vehicle.html")
    
    # Upload files to Firebase Storage
    bucket = storage.bucket(FirebaseConfig.STORAGE_BUCKET)
    
    # Generate a unique registration ID using timestamp
    registration_id = f"{student_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    vehicle_approve_ref = db.reference("vehicle_registration_approved")
    existing_registration = vehicle_approve_ref.child(student_id).get()
    if existing_registration:
        if (existing_registration.get("plate_number", "") == plate_number and 
            existing_registration.get("certificate", "") == certificate and 
            existing_registration.get("receipt", "") == receipt):
            flash("Vehicle already registered", category="error")
            return redirect(url_for("vehicle_registration.verify_vehicle"))
    
    # Change the reference to store multiple vehicles
    vehicle_ref = db.reference("vehicle_registration")
    
    # Determine the correct reference based on type
    if type == "student":
        student_ref = db.reference("Students").child(student_id)
    else:
        student_ref = db.reference("Employees").child(student_id)
    student = student_ref.get()
    
    # Check if required fields exist
    first_name = student.get("first_name", "")  
    last_name = student.get("last_name", "")
    full_name = f"{first_name} {last_name}".strip()
    image_url = student["image_url"]
    
    # Upload files with unique identifiers
    def upload_file(file, registration_id, file_type):
        if file:
            extension = file.filename.split('.')[-1].lower()
            content_type = "application/pdf" if extension == "pdf" else f"image/{extension}"
            blob = bucket.blob(f"Vehicle_registration/{registration_id}_{file_type}.{extension}")
            blob.upload_from_file(file, content_type=content_type)
            blob.make_public()
            return blob.public_url
        return None
    
    vehicle_orcr_url = upload_file(vehicle_orcr, registration_id, "vehicle_orcr")
    license_card_url = upload_file(license_card, registration_id, "license_card")
    vehicle_photo_url = upload_file(vehicle_photo, registration_id, "vehicle_photo")
    
    # Store the registration under a unique ID while maintaining student reference
    registration_data = {
        "type": type,
        "registration_id": registration_id,
        "student_id": student_id,
        "owner_name": full_name,
        "image_url": image_url,
        "contact_no": contact_no,
        "drivers_license": drivers_license,
        "day_issued": day_issued,
        "month_issued": month_issued,
        "year_issued": year_issued,
        "day_expiry": day_expiry,
        "month_expiry": month_expiry,
        "year_expiry": year_expiry,
        "vehicle_type": vehicle_type,
        "vehicle_make": vehicle_make,
        "vehicle_model": vehicle_model,
        "vehicle_year": vehicle_year,
        "plate_number": plate_number,
        "color": color,
        "certificate": certificate,
        "day_cert_issued": day_cert_issued,
        "month_cert_issued": month_cert_issued,
        "year_cert_issued": year_cert_issued,
        "receipt": receipt,
        "day_receipt_issued": day_receipt_issued,
        "month_receipt_issued": month_receipt_issued,
        "year_receipt_issued": year_receipt_issued,
        "driver_name": driver_name,
        "license_number": license_number,
        "date_issued": date_issued,
        "expiry_date": expiry_date,
        "relationship": relationship,
        "vehicle_orcr": vehicle_orcr_url,
        "license_card": license_card_url,
        "vehicle_photo": vehicle_photo_url,
        "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending"
    }
    
    # Store under a new unique registration ID
    vehicle_ref.child(registration_id).set(registration_data)

    flash("Registration submitted successfully", category="success")
    return redirect(url_for("vehicle_registration.verify_vehicle"))

@bp.route("/api/approve-registration", methods=["POST"])
def approve_registration():
    student_id = request.form.get("studentId")
    sticker_number = request.form.get("sticker_number")
    
    vehicle_approve_ref = db.reference("vehicle_registration_approved")
    vehicle_reject_ref = db.reference("vehicle_registration_rejected")
    vehicle_ref = db.reference("vehicle_registration").child(student_id)
    
    # Retrieve the student's registration data
    registration_data = vehicle_ref.get()
    
    if not registration_data:
        return jsonify({"message": "Registration not found"}), 404
    
    # Check if the registration exists in the rejected reference and delete it
    if vehicle_reject_ref.child(student_id).get():
        vehicle_reject_ref.child(student_id).delete()
    
    # Add to approved reference
    vehicle_approve_ref.child(student_id).set({
        "registration_id": student_id,
        "sticker_number": sticker_number,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **registration_data,
        "status": "approved"
    })
    
    # Update the status in the main vehicle registration reference
    vehicle_ref.update({
        "status": "approved"
    })
    
    flash("Registration approved successfully", category="success")
    return jsonify({"message": "success"}), 200

@bp.route("/api/reject-registration", methods=["POST"])
def reject_registration():
    registration_id = request.form.get("studentId")
    reason = request.form.get("reason")
    
    vehicle_ref = db.reference("vehicle_registration").child(registration_id)
    vehicle_reject_ref = db.reference("vehicle_registration_rejected")
    vehicle_approve_ref = db.reference("vehicle_registration_approved")
    
    # Retrieve the student's registration data
    registration_data = vehicle_ref.get()
    
    if not registration_data:
        flash("Registration not found", category="error")
        return jsonify({"message": "Registration not found"}), 404
    
    # Add to rejected reference with status "rejected"
    vehicle_reject_ref.child(registration_id).set({
        "registration_id": registration_id,
        "reason": reason,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **registration_data,
        "status": "rejected"
    })
    
    # Update the status in the main vehicle registration reference
    vehicle_ref.update({
        "status": "rejected"
    })
    
    flash("Registration rejected successfully", category="success")
    return jsonify({"message": "success"}), 200