import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from firebase_admin import storage

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


    
# Example usage
if __name__ == "__main__":
    asyncio.run(generate_faces())