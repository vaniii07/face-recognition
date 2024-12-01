from flask import render_template, request
from flask_jwt_extended import get_jwt
from app.vehicle_registration import vehicle_registration_bp as bp
from firebase_admin import db
from app.main.jwt import refresh_token
@bp.route("/verify-vehicle")
def verify_vehicle():
    return render_template("verify_vehicle.html")

@bp.route("/register-form/<user_id>")
def register_form(user_id):
    userRef = db.reference("Students")
    user = userRef.child(user_id).get()
    return render_template("form.html", user=user)

@bp.route("/manage-stickers")
@refresh_token()
def manage_stickers():
    vehicle_ref = db.reference("vehicle_registration")
    vehicles = vehicle_ref.get()
    claims = get_jwt()
    
    current_user = {
        "full_name": claims["full_name"],
        "position": claims["position"]
    }
    return render_template("manage_stickers.html", vehicles=vehicles, current_user=current_user)

def sidebar():
    return render_template("sidebar.html")

@bp.route("/registration-result")
def registration_result():
    vehicle_approve_ref = db.reference("vehicle_registration_approved")
    vehicle_reject_ref = db.reference("vehicle_registration_rejected")
    vehicle_ref = db.reference("vehicle_registration")
    approved = vehicle_approve_ref.get() or {}
    rejected = vehicle_reject_ref.get() or {}
    
    records = []
    
    # Add approved vehicles with status
    for vehicle_id, vehicle_data in approved.items():
        vehicle = vehicle_ref.child(vehicle_id).get() or {}
        record = {**vehicle_data, **vehicle, "status": "approved"}
        records.append(record)
    
    # Add rejected vehicles with status
    for vehicle_id, vehicle_data in rejected.items():
        vehicle = vehicle_ref.child(vehicle_id).get() or {}
        record = {**vehicle_data, **vehicle, "status": "rejected"}
        records.append(record)
    
    return render_template("list.html", vehicles=records)


@bp.route("/approved")
@refresh_token()
def approved():
    vehicle_approve_ref = db.reference("vehicle_registration_approved")
    vehicle_ref = db.reference("vehicle_registration")
    
    approved = vehicle_approve_ref.get() or {}
    
    # Attach additional data from vehicle_registration reference
    for vehicle_id, vehicle_data in approved.items():
        vehicle = vehicle_ref.child(vehicle_id).get()
        if vehicle:
            approved[vehicle_id] = {**vehicle_data, **vehicle}
    
    claims = get_jwt()
    
    current_user = {
        "full_name": claims["full_name"],
        "position": claims["position"]
    }
    
    
    return render_template("approved.html", vehicles=approved, current_user=current_user)

@bp.route("/denied")
@refresh_token()
def denied():
    vehicle_reject_ref = db.reference("vehicle_registration_rejected")
    vehicle_ref = db.reference("vehicle_registration")
    rejected = vehicle_reject_ref.get() or {}
    
    for vehicle_id, vehicle_data in rejected.items():
        vehicle = vehicle_ref.child(vehicle_id).get()
        if vehicle:
            rejected[vehicle_id] = {**vehicle_data, **vehicle}
            
    claims = get_jwt()
    
    current_user = {
        "full_name": claims["full_name"],
        "position": claims["position"]
    }
    
    return render_template("denied.html", vehicles=rejected, current_user=current_user)