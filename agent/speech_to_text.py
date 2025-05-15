from pathlib import Path
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribe an audio file to text using OpenAI's Whisper model.
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
        
    Returns:
        str: The transcribed text
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Open the audio file
    with open(audio_file_path, "rb") as audio_file:
        # Create transcription
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    
    return transcript.text

if __name__ == "__main__":
    # Example usage
    audio_file_path = Path(__file__).parent / "speech.mp3"
    output_file_path = Path(__file__).parent / "transcription.txt"
    
    try:
        # Transcribe the audio
        transcription = transcribe_audio(str(audio_file_path))
        
        # Save the transcription to a text file
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(transcription)
            
        print(f"Transcription completed successfully!")
        print(f"Transcription saved to: {output_file_path}")
        print(f"Transcribed text: {transcription}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}") 