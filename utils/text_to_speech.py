import os
import uuid
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

client = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

def generate_mp3_response(text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb", model_id: str = "eleven_multilingual_v2") -> str:
    """
    Generates an .ogg audio response from text using ElevenLabs and saves it locally.

    Args:
        text (str): The text to convert.
        voice_id (str): ElevenLabs voice ID.
        model_id (str): ElevenLabs model ID.

    Returns:
        str: Local file path to the saved .mp3 file.
    """
    # Get the audio data as bytes
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id=model_id,
        output_format="mp3_22050_32"
    )
    
    # Convert generator to bytes
    audio_bytes = b"".join(chunk for chunk in audio)

    # Save to file
    file_path = f"/tmp/{uuid.uuid4()}.mp3"
    with open(file_path, "wb") as f:
        f.write(audio_bytes)

    return file_path
