import os
import cv2
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials, db, storage
import requests
from io import BytesIO
from PIL import Image
import numpy as np
from config import FirebaseConfig

# Initialize Firebase
cred = credentials.Certificate(r"serviceAccountKey.json")
database_url = FirebaseConfig.DATABASE_URL
storage_url = FirebaseConfig.STORAGE_BUCKET

firebase_admin.initialize_app(cred, {
    'databaseURL': database_url,
    'storageBucket': storage_url
})

# Fetch student data from Firebase Realtime Database
ref = db.reference('Students')
students = ref.get()

# Lists to hold images and student IDs
imgList = []
studentIds = []

def crop_face(image):
    face_locations = face_recognition.face_locations(image)
    if face_locations:
        top, right, bottom, left = face_locations[0]
        face_image = image[top:bottom, left:right]
        return face_image
    else:
        return None

# Download images from Firebase storage and collect image data
for student_id, student_data in students.items():
    # Skip archived students
    if student_data.get('archived', False):
        print(f"Skipping archived student ID: {student_id}")
        continue

    image_url = student_data.get('image_url')
    if not image_url:
        print(f"No image URL for student ID: {student_id}")
        continue

    response = requests.get(image_url)
    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Crop the face from the image
        cropped_face = crop_face(img)
        if cropped_face is not None:
            # Resize the cropped face to 1:1 aspect ratio (e.g., 256x256)
            cropped_face = cv2.resize(cropped_face, (256, 256))
            imgList.append(cropped_face)
            studentIds.append(student_id)
        else:
            print(f"Face not found in image for student ID: {student_id}")
    else:
        print(f"Failed to download image for student ID: {student_id}")

print("Student IDs:", studentIds)

# Function to find face encodings
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        try:
            encode = face_recognition.face_encodings(img_rgb)[0]
            encodeList.append(encode)
        except IndexError:
            print(f"Face not found in image: {img}")
    return encodeList

# Encode faces
print("Encoding started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding complete")

# Save encodings to file
with open("EncodeFile.p", 'wb') as file:
    pickle.dump(encodeListKnownWithIds, file)
print("Encodings saved to EncodeFile.p")