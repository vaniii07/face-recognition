import cv2
import face_recognition
from flask import Response
from app.v_recognition import bp_v_recognition as bp
import numpy as np
import time
import firebase_admin
from firebase_admin import credentials, storage

camera = cv2.VideoCapture(0)
# # Initialize Firebase
# cred = credentials.Certificate("path/to/your/firebase/credentials.json")
# firebase_admin.initialize_app(cred, {
#     'storageBucket': 'your-firebase-storage-bucket'
# })
# bucket = storage.bucket()

# camera = cv2.VideoCapture(0)

# def upload_to_firebase(image_path, image_name):
#     blob = bucket.blob(image_name)
#     blob.upload_from_filename(image_path)
#     blob.make_public()
#     return blob.public_url


def initialize_camera():
    global camera
    if camera is not None:
        camera.release()
    camera = cv2.VideoCapture(0)
    
def gen_frames():
    green_start_time = None  # Track the start time when the box turns green
    countdown_start_time = None  # Track the start time for the countdown

    while True:
        print('Capturing...')
        success, frame = camera.read()
        if not success:
            break
        else:
            # Mirror the frame
            frame = cv2.flip(frame, 1)
            
            # Resize frame for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Find all face locations in the current frame
            face_locations = face_recognition.face_locations(small_frame)
            face_landmarks_list = face_recognition.face_landmarks(small_frame)

            for face_location, face_landmarks in zip(face_locations, face_landmarks_list):
                top, right, bottom, left = face_location
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Calculate the area of the face
                face_area = (right - left) * (bottom - top)
                frame_area = frame.shape[0] * frame.shape[1]
                face_percentage = (face_area / frame_area) * 100

                # Check if face is looking center
                left_eye = face_landmarks['left_eye']
                right_eye = face_landmarks['right_eye']
                nose_bridge = face_landmarks['nose_bridge']

                left_eye_center = np.mean(left_eye, axis=0)
                right_eye_center = np.mean(right_eye, axis=0)
                nose_center = np.mean(nose_bridge, axis=0)

                face_center_x = (left_eye_center[0] + right_eye_center[0]) / 2
                frame_center_x = small_frame.shape[1] / 2

                is_centered = abs(face_center_x - frame_center_x) < frame_center_x * 0.1

                # Additional checks for side view
                eye_distance = np.linalg.norm(left_eye_center - right_eye_center)
                nose_to_left_eye = np.linalg.norm(nose_center - left_eye_center)
                nose_to_right_eye = np.linalg.norm(nose_center - right_eye_center)

                is_frontal = abs(nose_to_left_eye - nose_to_right_eye) < eye_distance * 0.2

                # Check brightness
                face_image = frame[top:bottom, left:right]
                gray_face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
                brightness = np.mean(gray_face_image)
                brightness_threshold = 100  # Adjust this threshold as needed

                # Determine the color of the box
                if face_percentage >= 19 and is_centered and is_frontal and brightness >= brightness_threshold:
                    box_color = (0, 255, 0)  # Green for detailed, clear, centered, and bright face
                    if green_start_time is None:
                        green_start_time = time.time()
                        countdown_start_time = time.time()
                    
                    elif time.time() - green_start_time >= 3:
                        # Capture the face image after 3 seconds of green
                        image_path = 'captured_face.jpg'
                        cv2.imwrite(image_path, face_image)
                        green_start_time = None  # Reset the timer after capturing
                        countdown_start_time = None  # Reset the countdown timer
                        camera.release()
                        break  # Stop the stream after capturing the image

                else:
                    box_color = (0, 0, 255)  # Red for not detailed, clear, centered, or bright face
                    green_start_time = None  # Reset the timer if criteria are not met
                    countdown_start_time = None  # Reset the countdown timer if criteria are not met

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)

                # Display countdown
                if countdown_start_time is not None:
                    elapsed_time = time.time() - countdown_start_time
                    countdown = 3 - int(elapsed_time)
                    if countdown > 0:
                        cv2.putText(frame, f"Hold still in {countdown}", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    else:
                        cv2.putText(frame, "Capturing...", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@bp.route('/video_feed')
def video_feed():
    initialize_camera()
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@bp.route('/capture', methods=['POST'])
def capture():
    success, frame = camera.read()
    if success:
        cv2.imwrite('captured_image.jpg', frame)
    return 'Image Captured'