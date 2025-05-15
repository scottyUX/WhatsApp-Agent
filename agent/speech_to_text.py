from pathlib import Path
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import asyncio
import sys

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def validate_audio_file(file_path: str) -> str:
    """
    Validate that the audio file exists and is accessible.
    
    Args:
        file_path (str): Path to the audio file
        
    Returns:
        str: Absolute path to the audio file
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    # Convert to absolute path
    abs_path = os.path.abspath(file_path)
    
    if not os.path.exists(abs_path):
        raise FileNotFoundError(
            f"Audio file not found: {abs_path}\n"
            f"Please make sure the file exists and you have the correct path."
        )
    
    return abs_path

async def transcribe_audio(audio_file_path: str) -> str:
    """
    Transcribe an audio file to text using OpenAI's Whisper model.
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
        
    Returns:
        str: The transcribed text
    """
    try:
        # Validate the file exists
        abs_path = validate_audio_file(audio_file_path)
        
        # Open the audio file
        with open(abs_path, "rb") as audio_file:
            # Create transcription
            transcript = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        return transcript
    except FileNotFoundError as e:
        print(f"File error: {str(e)}")
        raise
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        raise

async def save_transcription(text: str, output_path: str) -> None:
    """
    Save the transcribed text to a file.
    
    Args:
        text (str): The text to save
        output_path (str): Path where to save the text file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Transcription saved to: {output_path}")
    except Exception as e:
        print(f"Error saving transcription: {str(e)}")
        raise

async def main():
    # Get the default audio file path (speech.mp3 in the agent directory)
    default_audio_path = str(Path(__file__).parent / "speech.mp3")
    
    # Use command line argument if provided, otherwise use default
    audio_file_path = sys.argv[1] if len(sys.argv) > 1 else default_audio_path
    output_file_path = str(Path(__file__).parent / "transcription.txt")
    
    try:
        print(f"Processing audio file: {audio_file_path}")
        # Transcribe the audio
        transcription = await transcribe_audio(audio_file_path)
        
        # Save the transcription
        await save_transcription(transcription, output_file_path)
        
        print(f"Transcription completed successfully!")
        print(f"Transcribed text: {transcription}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 