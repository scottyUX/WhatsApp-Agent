import uuid
from typing import Optional, Union, List
from sqlalchemy.orm import Session

from app.database.entities import Connection


class ConnectionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: Union[str, uuid.UUID], channel: str, device_id: Optional[Union[str, uuid.UUID]] = None, ip_address: Optional[str] = None) -> Connection:
        # Convert string UUIDs to UUID objects if needed
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        if isinstance(device_id, str):
            device_id = uuid.UUID(device_id)
        
        connection = Connection(user_id=user_id, channel=channel, device_id=device_id, ip_address=ip_address)
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def save(self, connection: Connection) -> Connection:
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def get_by_id(self, connection_id: Union[str, uuid.UUID]) -> Optional[Connection]:
        if isinstance(connection_id, str):
            connection_id = uuid.UUID(connection_id)
        
        return self.db.query(Connection).filter(Connection.id == connection_id).first()

    def get_whatsapp_connection_by_user(self, user_id: Union[str, uuid.UUID]) -> Optional[Connection]:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        
        return self.db.query(Connection).filter(Connection.user_id == user_id, Connection.channel == "whatsapp").first()

    def get_by_user(self, user_id: Union[str, uuid.UUID]) -> List[Connection]:
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        
        return self.db.query(Connection).filter(Connection.user_id == user_id).order_by(Connection.created_at.desc()).all()

    def get_by_device_id(self, device_id: Union[str, uuid.UUID]) -> Optional[Connection]:
        """Get connection by device ID. Sorts by most recent and returns the first one."""
        if isinstance(device_id, str):
            device_id = uuid.UUID(device_id)

        return self.db.query(Connection).filter(Connection.device_id == device_id).order_by(Connection.created_at.desc()).first()

    def get_by_ip_address(self, ip_address: str) -> Optional[Connection]:
        """Get connections by IP address. Sorts by most recent."""
        return self.db.query(Connection).filter(Connection.ip_address == ip_address).order_by(Connection.created_at.desc()).first()
