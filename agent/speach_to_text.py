# =============================
# utils/speech_to_text.py
# =============================

import asyncio
import sys
from openai import AsyncOpenAI

openai = AsyncOpenAI()

async def transcribe_audio(file_path: str) -> None:
    try:
        with open(file_path, "rb") as audio_file:
            transcription = await openai.audio.transcriptions.create(
                file=audio_file,
                model="whisper-1",
                response_format="text"
            )
            print("📝 Transcription result:\n")
            print(transcription)
    except Exception as e:
        print(f" Transcription failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python speech_to_text.py path/to/audiofile.mp3")
    else:
        asyncio.run(transcribe_audio(sys.argv[1]))
transcribe_audio("speech.mp3")
