import uuid
from typing import Optional, Union, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.database.entities import ConsultantNote


class ConsultantNoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        patient_profile_id: Union[str, uuid.UUID],
        consultant_email: str,
        note_content: str,
        consultation_id: Optional[Union[str, uuid.UUID]] = None,
        note_type: str = "general",
        is_private: bool = False
    ) -> ConsultantNote:
        # Convert string UUIDs to UUID objects if needed
        if isinstance(patient_profile_id, str):
            patient_profile_id = uuid.UUID(patient_profile_id)
        if isinstance(consultation_id, str):
            consultation_id = uuid.UUID(consultation_id)

        now = datetime.now()
        note = ConsultantNote(
            id=str(uuid.uuid4()),
            patient_profile_id=patient_profile_id,
            consultant_email=consultant_email,
            note_content=note_content,
            consultation_id=consultation_id,
            note_type=note_type,
            is_private=is_private,
            created_at=now,
            updated_at=now
        )
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def save(self, note: ConsultantNote) -> ConsultantNote:
        note.updated_at = datetime.now()
        self.db.add(note)
        self.db.commit()
        self.db.refresh(note)
        return note

    def get_by_id(self, note_id: Union[str, uuid.UUID]) -> Optional[ConsultantNote]:
        if isinstance(note_id, str):
            note_id = uuid.UUID(note_id)
        return self.db.query(ConsultantNote).filter(ConsultantNote.id == note_id).first()

    def get_by_patient_profile_id(
        self, 
        patient_profile_id: Union[str, uuid.UUID],
        include_private: bool = False
    ) -> List[ConsultantNote]:
        if isinstance(patient_profile_id, str):
            patient_profile_id = uuid.UUID(patient_profile_id)
        
        query = self.db.query(ConsultantNote).filter(
            ConsultantNote.patient_profile_id == patient_profile_id
        )
        
        if not include_private:
            query = query.filter(ConsultantNote.is_private == False)
        
        return query.order_by(desc(ConsultantNote.created_at)).all()

    def get_by_consultation_id(
        self, 
        consultation_id: Union[str, uuid.UUID],
        include_private: bool = False
    ) -> List[ConsultantNote]:
        if isinstance(consultation_id, str):
            consultation_id = uuid.UUID(consultation_id)
        
        query = self.db.query(ConsultantNote).filter(
            ConsultantNote.consultation_id == consultation_id
        )
        
        if not include_private:
            query = query.filter(ConsultantNote.is_private == False)
        
        return query.order_by(desc(ConsultantNote.created_at)).all()

    def get_by_consultant_email(
        self, 
        consultant_email: str,
        include_private: bool = False
    ) -> List[ConsultantNote]:
        query = self.db.query(ConsultantNote).filter(
            ConsultantNote.consultant_email == consultant_email
        )
        
        if not include_private:
            query = query.filter(ConsultantNote.is_private == False)
        
        return query.order_by(desc(ConsultantNote.created_at)).all()

    def update(
        self,
        note_id: Union[str, uuid.UUID],
        note_content: Optional[str] = None,
        note_type: Optional[str] = None,
        is_private: Optional[bool] = None
    ) -> Optional[ConsultantNote]:
        note = self.get_by_id(note_id)
        if not note:
            return None
        
        if note_content is not None:
            note.note_content = note_content
        if note_type is not None:
            note.note_type = note_type
        if is_private is not None:
            note.is_private = is_private
        
        return self.save(note)

    def delete(self, note_id: Union[str, uuid.UUID]) -> bool:
        note = self.get_by_id(note_id)
        if not note:
            return False
        
        self.db.delete(note)
        self.db.commit()
        return True
