import uuid
from datetime import datetime
from typing import Optional, Union, List
from sqlalchemy.orm import Session

from app.database.entities import ConnectionChange


class ConnectionChangeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, from_user_id: Union[str, uuid.UUID], to_user_id: Union[str, uuid.UUID], action: str) -> ConnectionChange:
        # Convert string UUIDs to UUID objects if needed
        if isinstance(from_user_id, str):
            from_user_id = uuid.UUID(from_user_id)
        if isinstance(to_user_id, str):
            to_user_id = uuid.UUID(to_user_id)
        
        connection_change = ConnectionChange(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            action=action
        )
        self.db.add(connection_change)
        self.db.commit()
        self.db.refresh(connection_change)
        return connection_change

    def save(self, connection_change: ConnectionChange) -> ConnectionChange:
        self.db.add(connection_change)
        self.db.commit()
        self.db.refresh(connection_change)
        return connection_change

