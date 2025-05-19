import os
from io import BytesIO
import requests
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Load environment variables
load_dotenv()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")
if not TWILIO_ACCOUNT_SID:
        raise RuntimeError("Please set TWILIO_ACCOUNT_SID in your .env")
if not TWILIO_AUTH_TOKEN:
        raise RuntimeError("Please set TWILIO_AUTH_TOKEN in your .env")

# ElevenLabs credentials
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise RuntimeError("Please set ELEVENLABS_API_KEY in your .env")

# Initialize ElevenLabs client
eleven = ElevenLabs(api_key=ELEVENLABS_API_KEY)

def transcribe_twilio_media(media_url: str,
                             model_id: str = "scribe_v1",
                             language_code: str = None,
                             diarize: bool = False,
                             tag_audio_events: bool = False) -> str:
    """
    Downloads an OGG from Twilio, streams it into ElevenLabs STT, and returns the transcript.

    Args:
        media_url:     Full Twilio Media URL (e.g. https://api.twilio.com/2010-04-01/...)
        model_id:      ElevenLabs STT model (default: 'scribe_v1')
        language_code: ISO language code or None for auto-detect
        diarize:       Enable speaker diarization
        tag_audio_events: Tag laughs/applause

    Returns:
        Transcribed text.
    """
    # 1) Download the audio bytes from Twilio
    resp = requests.get(media_url, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
    print("resp", resp)
    resp.raise_for_status()
    ogg_bytes = resp.content

    # 2) Stream into ElevenLabs Speech-to-Text
    audio_stream = BytesIO(ogg_bytes)
    print("audio_stream", audio_stream)
    
    # Ensure language_code is None for auto-detection
    if language_code is None:
        result = eleven.speech_to_text.convert(
            file=audio_stream,
            model_id=model_id,
            diarize=diarize,
            tag_audio_events=tag_audio_events
        )
    else:
        result = eleven.speech_to_text.convert(
            file=audio_stream,
            model_id=model_id,
            language_code=language_code,
            diarize=diarize,
            tag_audio_events=tag_audio_events
        )

    # 3) Return the transcript - access text directly from the Pydantic model
    return result.text if hasattr(result, 'text') else ""

if __name__ == "__main__":
    # Example usage with a placeholder URL
    url = "https://api.twilio.com/2010-04-01/Accounts/ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Messages/MMXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/Media/MEXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    transcript = transcribe_twilio_media(url, diarize=True, language_code=None, tag_audio_events=True)
    print("Transcript:\n", transcript)
