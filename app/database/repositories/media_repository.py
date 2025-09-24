import uuid
from typing import Optional, Union, List
from sqlalchemy.orm import Session

from app.database.entities import Media
from app.models.enums import MediaType


class MediaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        message_id: Union[str, uuid.UUID],
        media_type: MediaType,
        media_url: str,
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
        caption: Optional[str] = None
    ) -> Media:
        # Convert string UUID to UUID object if needed
        if isinstance(message_id, str):
            message_id = uuid.UUID(message_id)
        
        media = Media(
            message_id=message_id,
            media_type=media_type,
            media_url=media_url,
            filename=filename,
            file_size=file_size,
            mime_type=mime_type,
            caption=caption
        )
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)
        return media

    def save(self, media: Media) -> Media:
        self.db.add(media)
        self.db.commit()
        self.db.refresh(media)
        return media

    def get_by_message(self, message_id: Union[str, uuid.UUID]) -> List[Media]:
        # Convert string UUID to UUID object if needed
        if isinstance(message_id, str):
            message_id = uuid.UUID(message_id)
        
        return self.db.query(Media).filter(Media.message_id == message_id).order_by(Media.created_at.asc()).all()

    def get_by_id(self, media_id: Union[str, uuid.UUID]) -> Optional[Media]:
        # Convert string UUID to UUID object if needed
        if isinstance(media_id, str):
            media_id = uuid.UUID(media_id)
        
        return self.db.query(Media).filter(Media.id == media_id).first()
