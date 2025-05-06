import os
from pathlib import Path
import argparse
from dotenv import load_dotenv


"""
─────────────────────────────────────────────────────────────
📄 IstanbulMedic Translator: English ➜ German
─────────────────────────────────────────────────────────────
This script reads a medical text file written in English,
translates it into formal and fluent German using OpenAI GPT-4o,
and writes the translated output to a target file.

Usage:
    python translate_to_german.py --source <input_file.txt> --target <output_file.txt>

Notes:
- Replaces all mentions of "Longevita" with "IstanbulMedic".
- Maintains formatting including section separators (----).
- Suitable for medical policies, procedures, and formal content.

Author: Scott Davis
─────────────────────────────────────────────────────────────
"""


from openai import OpenAI
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.local.env'))

openai_api_key = os.getenv("OPENAI_API_KEY")
print(openai_api_key)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chunk_text(text, max_chars=3000):
    paragraphs = text.split("\n")
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) < max_chars:
            current += para + "\n"
        else:
            chunks.append(current.strip())
            current = para + "\n"
    if current:
        chunks.append(current.strip())
    return chunks

def translate_file(source_path: str, target_path: str):
    source_file = Path(source_path)
    target_file = Path(target_path)

    text = source_file.read_text().replace("Longevita", "IstanbulMedic")
    chunks = chunk_text(text)

    with open(target_file, "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            print(f"🔄 Translating chunk {i+1}/{len(chunks)}...")
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a professional medical translator. Translate the following English content into "
                            "formal, precise, and fluent German suitable for patients and healthcare professionals.\n\n"
                            "This document includes medical policies and procedures, and each section contains a URL that must be "
                            "preserved as-is. The document is divided by clear page breaks using --------------------------------------------------------------------------------.\n\n"
                            "Instructions:\n"
                            "- Translate all text faithfully, without summarizing, omitting, or adding any information.\n"
                            "- Keep URLs unchanged.\n"
                            "- Retain section and page structure as in the original.\n"
                            "- Use a consistent, professional tone throughout.\n"
                            "- Never include translation notes, metadata, or commentary."
                        )
                    },
                    {"role": "user", "content": chunk}
                ],
                temperature=0.2
            )
            translation = response.choices[0].message.content.strip()
            f.write(translation + "\n\n")

    print(f"✅ Translation complete. Output saved to: {target_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Translate an English medical file to German.")
    parser.add_argument("--source", required=True, help="Path to source .txt file")
    parser.add_argument("--target", required=True, help="Path to output translated file")

    args = parser.parse_args()
    translate_file(args.source, args.target)
