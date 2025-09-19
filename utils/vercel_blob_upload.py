# utils/vercel_blob.py
import os
import requests
from dotenv import load_dotenv
import vercel_blob
load_dotenv()

VERCEL_BLOB_TOKEN = os.getenv("VERCEL_BLOB_TOKEN")

def upload_file(file_path, blob_name):
    with open(file_path, 'rb') as f:
        response = vercel_blob.put(blob_name, f.read(), {"addRandomSuffix": "false"})
        print("✅ Upload successful!")
        print(f"📎 Blob URL: {response['url']}")
        print(f"⬇️ Download URL: {response['downloadUrl']}")

def main():
    upload_file("test.mp3", "test-1.mp3")

if __name__ == "__main__":
    main()