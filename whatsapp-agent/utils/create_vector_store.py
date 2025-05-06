"""
──────────────────────────────────────────────────────────────
📁 Vector Store Creator for IstanbulMedic
──────────────────────────────────────────────────────────────
Uploads a document to OpenAI and creates a vector store,
returning the vector store ID.

Usage:
    python create_vector_store.py --file path/to/translated_file.txt

Env:
    Requires OPENAI_API_KEY set via .env or export.

Author: Scott Davis
──────────────────────────────────────────────────────────────
"""

import os
import argparse
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_vector_store(file_path: str, log_path: str = "whatsapp-agent/data/vector_store_ids.txt"):
    print(f"📁 Creating vector store")
    file = client.files.create(
        file=Path(file_path).open("rb"),
        purpose="assistants"
    )
    print(f"✅ Uploaded file_id: {file.id}")

    store_name = f"Vector Store for {Path(file_path).name}"
    vector_store = client.beta.vector_stores.create(name=store_name)
    print(f"✅ Created vector_store_id: {vector_store.id}")

    client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id,
        files=[file.id]
    )
    print("✅ File added to vector store.")

    # 🔽 Append to vector_store_ids.txt
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{store_name} | ID: {vector_store.id}\n")

    return vector_store.id

create_vector_store(
    file_path="whatsapp-agent/data/IstanbulMedic_scraped_de.txt",
    log_path="whatsapp-agent/data/vector_store_ids.txt"
)



