import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.text_to_speech import generate_mp3_response
from utils.vercel_blob_upload import upload_file

def test_mp3_to_vercel():
    # Step 1: Generate OGG file
    text = "This is a test message from IstanbulMedic agent in audio format."
    ogg_path = generate_mp3_response(text)

    # Step 2: Upload to Vercel Blob
    blob_name = ogg_path.split("/")[-1]
    url = upload_file(ogg_path, blob_name)

    # Step 3: Output the result
    print(f"✅ Audio file uploaded successfully: {url}")

if __name__ == "__main__":
    test_mp3_to_vercel()
