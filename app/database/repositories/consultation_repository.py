import uuid
from typing import Optional, Union, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.exc import ProgrammingError, OperationalError

from app.database.entities import Consultation


class ConsultationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        zoom_meeting_id: str,
        topic: str,
        attendee_name: str,
        attendee_email: str,
        host_name: str,
        host_email: str,
        raw_payload: dict,
        patient_profile_id: Optional[Union[str, uuid.UUID]] = None,
        status: str = "scheduled",
        host_id: Optional[str] = None,
        agenda: Optional[str] = None,
        start_time: Optional[datetime] = None,
        duration: Optional[int] = None,
        timezone: Optional[str] = None,
        password: Optional[str] = None,
        join_url: Optional[str] = None,
        start_url: Optional[str] = None,
        attendee_phone: Optional[str] = None,
        host_join_token: Optional[str] = None,
        participant_join_token: Optional[str] = None,
        join_token_expires_at: Optional[datetime] = None,
        join_url_base: Optional[str] = None
    ) -> Consultation:
        # Convert string UUID to UUID object if needed
        if isinstance(patient_profile_id, str):
            patient_profile_id = uuid.UUID(patient_profile_id)

        now = datetime.now()
        consultation = Consultation(
            id=str(uuid.uuid4()),  # Generate ID
            patient_profile_id=patient_profile_id,
            zoom_meeting_id=zoom_meeting_id,
            host_id=host_id,
            topic=topic,
            agenda=agenda,
            status=status,
            start_time=start_time,
            duration=duration,
            timezone=timezone,
            password=password,
            join_url=join_url,
            start_url=start_url,
            attendee_name=attendee_name,
            attendee_email=attendee_email,
            attendee_phone=attendee_phone,
            raw_payload=raw_payload,
            host_join_token=host_join_token,
            participant_join_token=participant_join_token,
            join_token_expires_at=join_token_expires_at,
            join_url_base=join_url_base,
            host_name=host_name,
            host_email=host_email,
            created_at=now,  # Provide explicit timestamp
            updated_at=now   # Provide explicit timestamp
        )
        self.db.add(consultation)
        self.db.commit()
        self.db.refresh(consultation)
        return consultation

    def save(self, consultation: Consultation) -> Consultation:
        self.db.add(consultation)
        self.db.commit()
        self.db.refresh(consultation)
        return consultation

    def get_by_id(self, consultation_id: Union[str, uuid.UUID]) -> Optional[Consultation]:
        if isinstance(consultation_id, str):
            consultation_id = uuid.UUID(consultation_id)
        
        return self.db.query(Consultation).filter(Consultation.id == consultation_id).first()


    def get_by_patient_profile_id(self, patient_profile_id: Union[str, uuid.UUID]) -> List[Consultation]:
        if isinstance(patient_profile_id, str):
            patient_profile_id = uuid.UUID(patient_profile_id)

        return self.db.query(Consultation).filter(Consultation.patient_profile_id == patient_profile_id).all()

    def get_todays_consultations(self) -> List[Consultation]:
        """Get all consultations for today."""
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        try:
            return self.db.query(Consultation).filter(
                and_(
                    Consultation.start_time >= start_of_day,
                    Consultation.start_time <= end_of_day
                )
            ).order_by(Consultation.start_time).all()
        except (ProgrammingError, OperationalError) as exc:
            message = str(exc).lower()
            if "appoinment" in message or "appointment" in message:
                # Table not present (e.g. Cal.com sync disabled); treat as no consultations
                self.db.rollback()
                return []
            raise

    def get_upcoming_consultations(self, limit: int = 10) -> List[Consultation]:
        """Get upcoming consultations."""
        now = datetime.now()
        try:
            return self.db.query(Consultation).filter(
                Consultation.start_time > now
            ).order_by(Consultation.start_time).limit(limit).all()
        except (ProgrammingError, OperationalError) as exc:
            message = str(exc).lower()
            if "appoinment" in message or "appointment" in message:
                self.db.rollback()
                return []
            raise

    def update_status(self, cal_booking_id: str, status: str) -> Optional[Consultation]:
        """Update consultation status."""
        consultation = self.get_by_cal_booking_id(cal_booking_id)
        if consultation:
            consultation.status = status
            self.save(consultation)
        return consultation

    def delete_by_cal_booking_id(self, cal_booking_id: str) -> bool:
        """Delete consultation by Cal.com booking ID."""
        consultation = self.get_by_cal_booking_id(cal_booking_id)
        if consultation:
            self.db.delete(consultation)
            self.db.commit()
            return True
        return False
