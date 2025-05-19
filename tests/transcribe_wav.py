"""
Transcribe WAV File Script

This script provides a simple interface to transcribe WAV audio files using OpenAI's Whisper model
through the speech_to_text module. It's designed to be run as a standalone script for testing
or quick transcription of audio files.

Usage:
    python transcribe_wav.py

Dependencies:
    - openai: For the Whisper API
    - asyncio: For async/await functionality
    - agent.speech_to_text: Local module for transcription

Environment Variables Required:
    - OPENAI_API_KEY: Your OpenAI API key

Author: Scott Davis
Date: 2024
"""

import asyncio
import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from agent.speech_to_text import transcribe_audio

async def main():
    wav_file_path = "/var/folders/qj/4y7mx4c92bjdtmjgbzmn2dtr0000gn/T/tmp9tzf31gu.wav"
    
    try:
        # Transcribe the audio file
        transcription = await transcribe_audio(wav_file_path)
        print("Transcription:")
        print(transcription)
    except Exception as e:
        print(f"Error during transcription: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 