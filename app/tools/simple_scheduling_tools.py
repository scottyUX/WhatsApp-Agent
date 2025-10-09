"""
Simple scheduling tools for Istanbul Medic consultation booking
Simplified version that integrates with the knowledge agent
"""

from agents import function_tool
import datetime
import json
import os
from typing import Optional

# Try to import Google Calendar tools
try:
    from app.tools.google_calendar_tools import (
        create_calendar_event,
        list_upcoming_events,
        delete_event_by_title,
        reschedule_event_by_title
    )
    from app.tools.profile_tools import appointment_set
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    print("Warning: Calendar tools not available. Scheduling will be simulated.")

@function_tool
def schedule_consultation(
    patient_name: str,
    patient_email: str,
    patient_phone: str,
    preferred_date: str,
    preferred_time: str,
    timezone: str = "Europe/Istanbul"
) -> str:
    """
    Schedule a consultation appointment for Istanbul Medic.
    
    Args:
        patient_name: Full name of the patient
        patient_email: Email address for confirmation
        patient_phone: Phone number with country code
        preferred_date: Preferred date (YYYY-MM-DD format)
        preferred_time: Preferred time (HH:MM format)
        timezone: Timezone for the appointment (default: Europe/Istanbul)
    
    Returns:
        Confirmation message with appointment details
    """
    try:
        # Parse the date and time
        appointment_date = datetime.datetime.strptime(preferred_date, "%Y-%m-%d")
        appointment_time = datetime.datetime.strptime(preferred_time, "%H:%M").time()
        
        # Combine date and time
        appointment_datetime = datetime.datetime.combine(appointment_date.date(), appointment_time)
        
        # Convert to ISO format with timezone
        iso_datetime = appointment_datetime.isoformat() + "+03:00"  # Istanbul timezone
        iso_end = (appointment_datetime + datetime.timedelta(minutes=15)).isoformat() + "+03:00"
        
        if CALENDAR_AVAILABLE:
            # Create calendar event
            calendar_result = create_calendar_event(
                summary="Istanbul Medic Consultation",
                start_datetime=iso_datetime,
                duration_minutes=15,
                description=f"Istanbul Medic Specialist Appointment for {patient_name}",
                attendee_email=patient_email
            )
            
            # Set appointment in profile system
            appointment_result = appointment_set(
                iso_start=iso_datetime,
                iso_end=iso_end,
                tz=timezone,
                meet_link=calendar_result.get('meet_link', 'TBD'),
                notes=f"Free online consultation with Istanbul Medic specialist for {patient_name}. This is a no-obligation consultation to discuss hair transplant options."
            )
            
            return f"""✅ Consultation Scheduled Successfully!

📅 **Appointment Details:**
- **Date:** {appointment_date.strftime('%A, %B %d, %Y')}
- **Time:** {appointment_time.strftime('%I:%M %p')} ({timezone})
- **Duration:** 15 minutes
- **Type:** Free online consultation

👤 **Patient Information:**
- **Name:** {patient_name}
- **Email:** {patient_email}
- **Phone:** {patient_phone}

📧 **Confirmation:**
You will receive a confirmation email at {patient_email} with the meeting link and additional details.

📞 **Contact Us:**
If you need to reschedule or have questions:
- Phone: +90 216 418 1015
- WhatsApp: +90 532 277 15 71
- Email: info@istanbulmedic.com

We look forward to speaking with you!"""
        
        else:
            # Fallback when calendar tools are not available
            return f"""✅ Consultation Request Received!

📅 **Appointment Details:**
- **Date:** {appointment_date.strftime('%A, %B %d, %Y')}
- **Time:** {appointment_time.strftime('%I:%M %p')} ({timezone})
- **Duration:** 15 minutes
- **Type:** Free online consultation

👤 **Patient Information:**
- **Name:** {patient_name}
- **Email:** {patient_email}
- **Phone:** {patient_phone}

📧 **Next Steps:**
Our team will contact you within 24 hours to confirm your appointment and provide the meeting link.

📞 **Contact Us:**
If you need immediate assistance:
- Phone: +90 216 418 1015
- WhatsApp: +90 532 277 15 71
- Email: info@istanbulmedic.com

We look forward to speaking with you!"""
            
    except Exception as e:
        return f"❌ Error scheduling appointment: {str(e)}. Please contact us directly at +90 216 418 1015."

@function_tool
def check_availability(date: str) -> str:
    """
    Check available time slots for a specific date.
    
    Args:
        date: Date to check (YYYY-MM-DD format)
    
    Returns:
        Available time slots for the date
    """
    try:
        appointment_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        day_name = appointment_date.strftime('%A')
        
        # Basic availability check (simplified)
        if appointment_date.date() < datetime.date.today():
            return "❌ That date has already passed. Please select a future date."
        
        # Check if it's a weekend
        if day_name in ['Saturday', 'Sunday']:
            return "❌ We don't have consultations on weekends. Please select a weekday (Monday-Friday)."
        
        # Available time slots (simplified)
        available_slots = [
            "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"
        ]
        
        return f"""📅 **Available Time Slots for {appointment_date.strftime('%A, %B %d, %Y')}:**

🕘 **Morning Slots:**
- 9:00 AM
- 10:00 AM  
- 11:00 AM

🕐 **Afternoon Slots:**
- 2:00 PM
- 3:00 PM
- 4:00 PM
- 5:00 PM

Please let me know which time works best for you, and I'll help you schedule your consultation!"""
        
    except ValueError:
        return "❌ Invalid date format. Please use YYYY-MM-DD format (e.g., 2025-01-15)."
    except Exception as e:
        return f"❌ Error checking availability: {str(e)}"

@function_tool
def reschedule_appointment(
    patient_email: str,
    new_date: str,
    new_time: str,
    timezone: str = "Europe/Istanbul"
) -> str:
    """
    Reschedule an existing consultation appointment.
    
    Args:
        patient_email: Email address of the patient
        new_date: New date (YYYY-MM-DD format)
        new_time: New time (HH:MM format)
        timezone: Timezone for the appointment (default: Europe/Istanbul)
    
    Returns:
        Confirmation message with new appointment details
    """
    try:
        if CALENDAR_AVAILABLE:
            # Parse the new date and time
            appointment_date = datetime.datetime.strptime(new_date, "%Y-%m-%d")
            appointment_time = datetime.datetime.strptime(new_time, "%H:%M").time()
            appointment_datetime = datetime.datetime.combine(appointment_date.date(), appointment_time)
            iso_datetime = appointment_datetime.isoformat() + "+03:00"
            
            # Reschedule using the calendar tools
            result = reschedule_event_by_title(
                title="Istanbul Medic Consultation",
                new_start_datetime=iso_datetime,
                duration_minutes=15
            )
            
            return f"""✅ Appointment Rescheduled Successfully!

📅 **New Appointment Details:**
- **Date:** {appointment_date.strftime('%A, %B %d, %Y')}
- **Time:** {appointment_time.strftime('%I:%M %p')} ({timezone})
- **Duration:** 15 minutes

📧 **Confirmation:**
You will receive a confirmation email at {patient_email} with the updated meeting details.

📞 **Contact Us:**
If you need further assistance:
- Phone: +90 216 418 1015
- WhatsApp: +90 532 277 15 71
- Email: info@istanbulmedic.com"""
        
        else:
            return f"""✅ Reschedule Request Received!

📅 **New Appointment Details:**
- **Date:** {appointment_date.strftime('%A, %B %d, %Y')}
- **Time:** {appointment_time.strftime('%I:%M %p')} ({timezone})
- **Duration:** 15 minutes

📧 **Next Steps:**
Our team will contact you within 24 hours to confirm the rescheduled appointment.

📞 **Contact Us:**
If you need immediate assistance:
- Phone: +90 216 418 1015
- WhatsApp: +90 532 277 15 71
- Email: info@istanbulmedic.com"""
            
    except ValueError:
        return "❌ Invalid date or time format. Please use YYYY-MM-DD for date and HH:MM for time."
    except Exception as e:
        return f"❌ Error rescheduling appointment: {str(e)}. Please contact us directly at +90 216 418 1015."

@function_tool
def cancel_appointment(patient_email: str) -> str:
    """
    Cancel an existing consultation appointment.
    
    Args:
        patient_email: Email address of the patient
    
    Returns:
        Confirmation message for cancellation
    """
    try:
        if CALENDAR_AVAILABLE:
            # Cancel using the calendar tools
            result = delete_event_by_title("Istanbul Medic Consultation")
            
            return f"""✅ Appointment Cancelled Successfully!

📧 **Confirmation:**
Your consultation appointment has been cancelled. You will receive a confirmation email at {patient_email}.

🔄 **Reschedule:**
If you'd like to reschedule for a different time, please let me know and I'll be happy to help you find a new appointment slot.

📞 **Contact Us:**
If you have any questions:
- Phone: +90 216 418 1015
- WhatsApp: +90 532 277 15 71
- Email: info@istanbulmedic.com"""
        
        else:
            return f"""✅ Cancellation Request Received!

📧 **Confirmation:**
Your consultation appointment cancellation request has been received. Our team will process this within 24 hours and send confirmation to {patient_email}.

🔄 **Reschedule:**
If you'd like to reschedule for a different time, please let me know and I'll be happy to help you find a new appointment slot.

📞 **Contact Us:**
If you have any questions:
- Phone: +90 216 418 1015
- WhatsApp: +90 532 277 15 71
- Email: info@istanbulmedic.com"""
            
    except Exception as e:
        return f"❌ Error cancelling appointment: {str(e)}. Please contact us directly at +90 216 418 1015."

print("🟦 SIMPLE SCHEDULING TOOLS: Loaded scheduling functions for Istanbul Medic consultations")
