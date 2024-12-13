from asyncio import subprocess
import os
import pickle
import cv2
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials, db, storage
from datetime import datetime
from twilio.rest import Client
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config, FirebaseConfig
import asyncio
from concurrent.futures import ThreadPoolExecutor
# Initialize Firebase
service_account_path = os.path.join(os.getcwd(), "serviceAccountKey.json")

cred = credentials.Certificate(service_account_path)
database_url = FirebaseConfig.DATABASE_URL
storage_url = FirebaseConfig.STORAGE_BUCKET
print(f"Database URL: {database_url}")
print(f"Storage URL: {storage_url}")

firebase_admin.initialize_app(cred, {
    'databaseURL': database_url,
    'storageBucket':  storage_url
})

# Initialize Twilio client
# client = Client(keys.account_sid, keys.auth_token)
bucket = storage.bucket()

executor = ThreadPoolExecutor()


async def download_file_from_storage(file_path="EncodeFile.p"):
    loop = asyncio.get_event_loop()
    # Create a blob (file object) in the bucket
    blob = bucket.blob(f"encoded_files/{os.path.basename(file_path)}")
    
    # Download the file
    await loop.run_in_executor(executor, blob.download_to_filename, file_path)
    
    print(f"File downloaded to {file_path}")


def validate_phone_number(phone_number):
    phone_number = str(phone_number)
    
    # Remove leading zero if present
    if phone_number.startswith("0"):
        phone_number = phone_number[1:]
    
    # Ensure the number is 10 or 11 digits long
    if len(phone_number) < 10 or len(phone_number) > 11:
        print(f"Invalid phone number length: {phone_number}")
        return None
    
    # Add 63 if not already present
    if not phone_number.startswith("+63"):
        phone_number = "+63" + phone_number
    
    return phone_number

async def send_email(recipient_email, student_name, attendance_type):
    # Email content
    subject = "Attendance Notification"
    body = f'Good Day, We are pleased to inform you that {student_name} has {attendance_type} at Urdaneta City University'

    # Email setup
    sender_email = Config.GMAIL_EMAIL
    sender_password = Config.GMAIL_APP_PASSWORD

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, send_email_sync, sender_email, sender_password, recipient_email, msg)
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

def get_today_count(student_id, monitoring_ref):
    current_date = datetime.now().strftime("%Y-%m-%d")
    # Query monitoring data for the specific student_id and today's date
    student_monitoring_data = monitoring_ref.order_by_child("student_id").equal_to(student_id).get()
    if not student_monitoring_data:
        return 0
        
    count = sum(1 for key, data in student_monitoring_data.items() 
                if data.get("updated_time", "").startswith(current_date) and data.get("attendance_type") == "entered")
    print(f"Today's count for student {student_id}: {count}")  # Debug print
    return count

def get_exit_count(student_id, monitoring_ref):
    current_date = datetime.now().strftime("%Y-%m-%d")
    # Query monitoring data for the specific student_id and today's date
    student_monitoring_data = monitoring_ref.order_by_child("student_id").equal_to(student_id).get()
    if not student_monitoring_data:
        return 0
    
    count = sum(1 for key, data in student_monitoring_data.items() 
                if data.get("updated_time", "").startswith(current_date) and data.get("attendance_type") == "exited")
    print(f"Today's exit count for student {student_id}: {count}")  # Debug print
    return count

def send_email_sync(sender_email, sender_password, recipient_email, msg):
    server = smtplib.SMTP('smtp.gmail.com', 587)  # Replace with your SMTP server and port
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()

async def send_message(phone_number, student_name, attendance_type):
    phone_number = validate_phone_number(phone_number)
    if phone_number is None:
        print(f"Invalid phone number: {phone_number}")
        return

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, _send_message, phone_number, student_name, attendance_type)

def _send_message(phone_number, student_name, attendance_type):
    try:
        account_sid = Config.ACCOUNT_SID
        auth_token = Config.AUTH_TOKEN
        client = Client(account_sid, auth_token)

        # Get the current date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message_body = f"Good Day,\n\nWe are writing to inform you that {student_name} has been {attendance_type} at Urdaneta City University on {current_datetime}."
        message = client.messages.create(
            messaging_service_sid=Config.TWILIO_MESSAGING_SERVICE_SID,
            body=message_body,
            to=phone_number
        )

        print(f"Notification sent to {phone_number}: {message.sid}")
    except Exception as e:
        print(f"Failed to send message to {phone_number}: {e}")
        
async def load_encode_file():
    print("Running EncodeGenerator.py...")
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, os.system, "python EncodeGenerator.py")

    print("Loading Encode File")
    with open('EncodeFile.p', 'rb') as file:
        encodeListKnownWithIds = pickle.load(file)
    encodeListKnown, studentIds = encodeListKnownWithIds
    print("Encode File Loaded")
    print(f"Loaded {len(encodeListKnown)} known faces with IDs.")
    return encodeListKnown, studentIds

async def update_student_info(id):
    loop = asyncio.get_event_loop()
    studentInfo = await loop.run_in_executor(executor, db.reference(f'Students/{id}').get)
    print(f"Student Info: {studentInfo}")
    monitoring_ref = db.reference('monitoring')

    if not studentInfo:
        print(f"No student info found for ID: {id}")
        return None, None, None, None

    datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_time = datetime.now().strftime("%H:%M:%S")
    
    if studentInfo:
        blob = await loop.run_in_executor(executor, bucket.get_blob, f'Images/{id}.jpg')
        if blob:
            array = np.frombuffer(await loop.run_in_executor(executor, blob.download_as_string), np.uint8)
            imgStudent = cv2.imdecode(array, cv2.IMREAD_COLOR)
        else:
            imgStudent = None
            print(f"Image for ID {id} not found in Firebase storage.")
        
        if 'last_entered_time' in studentInfo and studentInfo['last_entered_time']:
            datetimeObject = datetime.strptime(studentInfo['last_entered_time'], "%Y-%m-%d %H:%M:%S")
        else:
            datetimeObject = datetime.now()
            studentInfo['last_entered_time'] = datetime_now
            await loop.run_in_executor(executor, db.reference(f'Students/{id}').child('last_entered_time').set, studentInfo['last_entered_time'])

        secondsElapsed = (datetime.now() - datetimeObject).total_seconds()

        if secondsElapsed > 30:
            ref = db.reference(f'Students/{id}')
            current_total = studentInfo.get('total_entered', 0)
            studentInfo['total_entered'] = current_total + 1
            await loop.run_in_executor(executor, ref.child('total_entered').set, studentInfo['total_entered'])
            await loop.run_in_executor(executor, ref.child('last_entered_time').set, datetime_now)
            course = studentInfo.get('course', '')
            current_date = datetime.now().strftime("%Y-%m-%d")
            attendance_ref = db.reference(f'attendance/{course}/{current_date}/{id}')
            attendance_data = await loop.run_in_executor(executor, attendance_ref.get)
            full_name = f"{studentInfo.get('first_name', '')} {studentInfo.get('middle_initial', '')} {studentInfo.get('middle_name', '')} {studentInfo.get('last_name', '')}".strip()

            # Determine if this is an entry or exit
            attendance_type = 'entered'  # Default to entry
            if attendance_data:
                for key, entry in attendance_data.items():
                    if 'time_in' in entry and ('time_out' not in entry or not entry['time_out']):
                        # If there's an entry without exit, this is an exit
                        await loop.run_in_executor(executor, attendance_ref.child(key).update, {'time_out': current_time})
                        attendance_type = 'exited'
                        break
                    else:
                        # No open entries found, this is a new entry    
                        new_entry = attendance_ref.push()
                        await loop.run_in_executor(executor, new_entry.set, {
                            'time_in': current_time,
                            'time_out': ''
                        })
            else:
                # No open entries found, this is a new entry    
                new_entry = attendance_ref.push()
                await loop.run_in_executor(executor, new_entry.set, {
                    'time_in': current_time,
                    'time_out': ''
                })


            # Send message with correct attendance type
            await send_message(studentInfo['phone'], full_name, attendance_type)

            studentInfo['time_in'] = current_time
            
            full_name = f"{studentInfo.get('first_name', '')} {studentInfo.get('middle_name', '')} {studentInfo.get('last_name', '')}".strip()
            monitoring_ref = db.reference('monitoring')
            datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await loop.run_in_executor(executor, monitoring_ref.child(datetime_now).set, {
                'student_id': id,
                'name': full_name,
                'course': studentInfo.get('course', ''),
                'program': studentInfo.get('program', ''),
                'image_url': studentInfo.get('image_url', ''),
                'updated_time': datetime_now,
                'attendance_type': attendance_type
            })
            
            today_count = get_today_count(id, monitoring_ref)
            today_exits = get_exit_count(id, monitoring_ref)
        else:
            print("Student already entered within the last 30 seconds")
            studentInfo = None
            imgStudent = None
            today_count = None
            today_exits = None

        return studentInfo, imgStudent, today_count, today_exits
    else:
        print(f"No student info found for ID: {id}")
        return None, None, None, None

def process_faces(frame, encodeListKnown, studentIds):
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_data = []
    for face_encoding, face_location in zip(face_encodings, face_locations):
        matches = face_recognition.compare_faces(encodeListKnown, face_encoding, tolerance=0.4)
        face_distance = face_recognition.face_distance(encodeListKnown, face_encoding)
        match_index = np.argmin(face_distance)

        if matches[match_index] and face_distance[match_index] < 0.4:
            face_data.append((face_location, studentIds[match_index], True))
        else:
            face_data.append((face_location, None, False))

    return face_data

async def main():
    process_this_frame = True

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    imgBackground = cv2.imread('Resources/background.png')

    folderModePath = 'Resources/Modes'
    if not os.path.exists(folderModePath):
        print(f"Error: Directory '{folderModePath}' does not exist")
        return

    modePathList = os.listdir(folderModePath)
    imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList if
                   cv2.imread(os.path.join(folderModePath, path)) is not None]

    if not cap.isOpened():
        print("Error: Camera not accessible")
        return

    encodeListKnown, studentIds = await load_encode_file()
    modeType = 0
    counter = 0
    id = None
    imgStudent = None
    face_data = []
    current_match_data = None
    last_student_info = None
    last_img_student = None

    while True:
        success, img = cap.read()

        if not success:
            print("Failed to capture image")
            break

        imgBackground[162:162 + img.shape[0], 55:55 + img.shape[1]] = img
        
        if imgModeList:
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        if process_this_frame:
            face_data = process_faces(img, encodeListKnown, studentIds)
            
        process_this_frame = not process_this_frame

        if face_data:
            for faceLoc, studentId, isMatch in face_data:
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1

                if isMatch:
                    bbox_color = (0, 255, 0)
                    text = "Match"
                else:
                    bbox_color = (0, 0, 255)
                    text = "No Match"

                cv2.rectangle(imgBackground, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), bbox_color, 2)
                cv2.putText(imgBackground, text, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, bbox_color, 2)

                if isMatch:
                    if current_match_data != (studentId, faceLoc):
                        current_match_data = (studentId, faceLoc)
                        id = studentId
                        if counter == 0:
                            cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                            cv2.waitKey(1)
                            counter = 1
                            modeType = 1
                        
                        if counter == 3 and id is not None:
                            modeType = 2
                            studentInfo, imgStudent, today_count, today_exits = await update_student_info(id)
                            if studentInfo:
                                print(f"Student Info: {studentInfo}")
                                last_student_info = studentInfo
                                last_img_student = imgStudent

                            if studentInfo is None:
                                modeType = 3
                                counter = 0
                                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                                
                        if counter >= 3:
                            if studentInfo:
                                # Get current time and date
                                current_time = datetime.now().strftime("%H:%M:%S")
                                current_date = datetime.now().strftime("%Y-%m-%d")
                                
                                cv2.putText(imgBackground, f"Entries: {today_count}", (861, 125),
                                           cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 0), 1)
                                cv2.putText(imgBackground, f"Exits: {today_exits}", (861, 155),
                                           cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 0), 1)
                                cv2.putText(imgBackground, str(studentInfo.get('program')), (1010, 558),
                                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)
                                cv2.putText(imgBackground, str(id), (1010, 498),
                                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)
                                cv2.putText(imgBackground, str(studentInfo.get('gender')), (910, 625),
                                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                                cv2.putText(imgBackground, str(studentInfo.get('school_year')), (1025, 625),
                                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                                cv2.putText(imgBackground, current_time, (1125, 625),
                                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                                cv2.putText(imgBackground, current_date, (1010, 590),  
                                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                                name = studentInfo.get('first_name') + " " + studentInfo.get('middle_initial') + " " + studentInfo.get('last_name')
                                (w, h), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                                offset = (414 - w) // 2
                                cv2.putText(imgBackground, str(name), (808 + offset, 445),
                                            cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                                if imgStudent is not None:
                                    imgStudent = cv2.resize(imgStudent, (216, 216))
                                    imgBackground[175:391, 909:1125] = imgStudent
                                    cv2.imshow("Face Recognition", imgBackground)
                                    cv2.waitKey(3000)
                                    
                                    imgBackground[175:391, 909:1125] = (0, 0, 0)
                                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
                                    cv2.imshow("Face Recognition", imgBackground)
                                    
                                studentInfo = None
                        print(f"Counter: {counter}")
                        counter += 1
                        if counter >= 20:
                            counter = 0
                            modeType = 0
                            studentInfo = None
                            imgStudent = None
                            face_data = []
                            
        else:
            counter = 0

        cv2.imshow("Face Recognition", imgBackground)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(main())