import os
from io import BytesIO
import requests
from elevenlabs.client import ElevenLabs
from app.config.settings import settings

eleven = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

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
    resp = requests.get(media_url, auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN))
    print("resp", resp)
    resp.raise_for_status()
    ogg_bytes = resp.content

    audio_stream = BytesIO(ogg_bytes)
    print("audio_stream", audio_stream)
    
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

    return result.text if hasattr(result, 'text') else ""
