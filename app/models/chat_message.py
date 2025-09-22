from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class ChatMessageRequest:
    content: Optional[str] = None
    media_urls: Optional[List[str]] = None
    audio_urls: Optional[List[str]] = None


@dataclass
class ChatMessageResponse:
    content: str
