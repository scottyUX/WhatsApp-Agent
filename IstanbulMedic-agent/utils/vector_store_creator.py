import openai
import os

from dotenv import load_dotenv

# Set your OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")  # or directly: openai.api_key = "your-api-key"

filepath = "longevita_scraped.txt" 
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")  # or replace with your actual key

def upload_file(file_path):
    with open(file_path, "rb") as f:
        file = openai.files.create(file=f, purpose="assistants")
    print(f"✅ Uploaded file_id: {file.id}")
    return file.id

def create_vector_store(file_id, name="Longevita RAG Store", description="Website data for RAG agent"):
    vs = openai.vector_stores.create(
        name=name,
        #description=description,
        file_ids=[file_id]
    )
    print(f"✅ Created vector_store_id: {vs.id}")
    return vs.id

if __name__ == "__main__":
    file_path = "longevita_scraped.txt"  # Path to your file

    try:
        file_id = upload_file(file_path)
        vector_store_id = create_vector_store(file_id)
    except Exception as e:
        print(f"❌ Error: {e}")



upload_file(filepath)