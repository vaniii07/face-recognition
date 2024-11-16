from flask import jsonify, redirect, url_for
from app import app

@app.errorhandler(401)
def custom_401_error(error):
    return redirect(url_for("main.login_page"))

# @app.errorhandler(Exception)
# def handle_all_errors(error):
#     # Log the error or perform any other necessary actions
#     app.logger.error(f"An error occurred: {error}")

#     # Return a custom JSON response or redirect
#     response = jsonify(message="An unexpected error occurred", error=str(error))
#     response.status_code = 500  # Internal Server Error
#     return response