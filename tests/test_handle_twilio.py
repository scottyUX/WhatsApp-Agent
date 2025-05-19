import pytest
from fastapi.datastructures import FormData
from data.handle_twilio import handle_audio_urls
import os
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_form_data():
    form = FormData()
    form._dict = {
        "NumMedia": "1",
        "MediaContentType0": "audio/ogg",
        "MediaUrl0": "https://api.twilio.com/2010-04-01/Accounts/AC123/Messages/MM123/Media/ME123"
    }
    return form

def test_handle_audio_urls(mock_form_data):
    # Get the path to the test .ogg file
    test_ogg_path = os.path.join(os.path.dirname(__file__), 'data', 'test.ogg')
    
    # Mock the requests.get response with real file content
    with open(test_ogg_path, 'rb') as f:
        mock_response = MagicMock()
        mock_response.content = f.read()
    
    with patch('requests.get', return_value=mock_response) as mock_get:
        wav_paths = handle_audio_urls(mock_form_data)
        
        # Verify the request was made with correct auth
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs['auth'] == (os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        
        # Verify we got a WAV file path back
        assert len(wav_paths) == 1
        assert wav_paths[0].endswith('.wav')
        
        # Verify the WAV file was created and has content
        assert os.path.exists(wav_paths[0])
        assert os.path.getsize(wav_paths[0]) > 0
        
        # Clean up the test WAV file
        if os.path.exists(wav_paths[0]):
            os.remove(wav_paths[0]) 