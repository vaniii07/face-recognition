import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from firebase_admin import storage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config
import smtplib

async def generate_faces():
    # Run the EncodeGenerator.py script
    await run_encode_generator()
    
    # Path to the encoded file
    encoded_file_path = "EncodeFile.p"
    
    # Check if the file exists
    if os.path.exists(encoded_file_path):
        # Upload the file to Firebase Storage
        await upload_file_to_storage(encoded_file_path)
    else:
        print("Encoded file not found.")

async def run_encode_generator():
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, os.system, "python EncodeGenerator.py")

async def upload_file_to_storage(file_path):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, _upload_file, file_path)
        

def _upload_file(file_path):
    # Reference to the Firebase Storage bucket
    bucket = storage.bucket()
    
    # Create a blob (file object) in the bucket
    blob = bucket.blob(f"encoded_files/{os.path.basename(file_path)}")
    
    # Upload the file
    blob.upload_from_filename(file_path)
    
    # Make the file publicly accessible (optional)
    blob.make_public()
    
    print(f"File uploaded to {blob.public_url}")
    
    
def send_email(recipient_email, username, password):
    """Send attendance notification email synchronously"""
    # Email content
    subject = "Account Creation Successful"
    body = f'Greetings {username},\n\nYour account has been successfully created.\n\nUsername: {username}\nPassword: {password}\n\nThank you for using our service.\n\nBest regards,\nCode Breaker Team'

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
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")
    
