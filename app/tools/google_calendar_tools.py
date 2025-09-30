try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False
    print("Warning: Google Calendar API not available. Calendar functions will be disabled.")
from agents import function_tool
import datetime
import os
import uuid

SCOPES = [
    'https://www.googleapis.com/auth/calendar.events',
    'https://www.googleapis.com/auth/calendar.events.readonly'
]

def get_calendar_service():
    if not GOOGLE_CALENDAR_AVAILABLE:
        raise RuntimeError('Google Calendar API is not available. Please install google-api-python-client.')
    
    import json
    
    # Try to use GOOGLE_SERVICE_ACCOUNT_JSON first (for Vercel deployment)
    service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
    
    if service_account_json:
        try:
            # Parse the JSON string
            info = json.loads(service_account_json)
            creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
            delegated_user = os.getenv('GOOGLE_CALENDAR_ID')
            if delegated_user:
                creds = creds.with_subject(delegated_user)
            return build('calendar', 'v3', credentials=creds)
        except json.JSONDecodeError as e:
            raise RuntimeError(f'Invalid GOOGLE_SERVICE_ACCOUNT_JSON: {e}')
    
    # Fallback to individual environment variables (for local development)
    private_key = os.getenv('GOOGLE_PRIVATE_KEY')
    client_email = os.getenv('GOOGLE_CLIENT_EMAIL')
    project_id = os.getenv('GOOGLE_PROJECT_ID')

    if not private_key or not client_email:
        raise RuntimeError('Missing Google service account credentials in environment (.env)')

    # Handle escaped newlines in private key
    private_key = private_key.replace('\\n', '\n')

    info = {
        "type": "service_account",
        "project_id": project_id or "project",
        "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID'),
        "private_key": private_key,
        "client_email": client_email,
        "client_id": os.getenv('GOOGLE_CLIENT_ID'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv('GOOGLE_CLIENT_X509_CERT_URL')
    }

    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    delegated_user = os.getenv('GOOGLE_CALENDAR_ID')
    if delegated_user:
        creds = creds.with_subject(delegated_user)

    return build('calendar', 'v3', credentials=creds)

@function_tool
def create_calendar_event(summary: str, start_datetime: str, duration_minutes: int = 60, description: str = None, attendee_email: str = None) -> str:
    """
    Create a calendar event with optional Google Meet link and attendee invitation.
    
    Args:
        summary (str): Event title/summary
        start_datetime (str): Start time in ISO format (e.g., '2024-01-15T14:00:00')
        duration_minutes (int): Duration in minutes (default: 60)
        description (str): Event description (optional)
        attendee_email (str): Email address to invite as attendee (optional)
    
    Returns:
        str: Confirmation message with event details and Google Meet link (if generated)
    
    Features:
        - Automatically generates Google Meet link when attendee_email is provided
        - Sends calendar invitation to attendee
        - Returns event time and Meet link for easy sharing
    """
    if not GOOGLE_CALENDAR_AVAILABLE:
        return "Calendar functionality is currently unavailable. Please contact our team directly to schedule your appointment."
    
    print(f"🔴 CREATE_CALENDAR_EVENT: Called with summary={summary}, start_datetime={start_datetime}")
    print(f"🔴 CREATE_CALENDAR_EVENT: duration_minutes={duration_minutes}, attendee_email={attendee_email}")
    
    try:
        service = get_calendar_service()
        start = datetime.datetime.fromisoformat(start_datetime)
        end = start + datetime.timedelta(minutes=duration_minutes)
        print(f"🔴 CREATE_CALENDAR_EVENT: Parsed start={start}, end={end}")

        # Base event structure
        event = {
            'summary': summary,
            'description': description or 'Scheduled via Calendar Agent',
            'start': {'dateTime': start.isoformat(), 'timeZone': 'America/New_York'},
            'end': {'dateTime': end.isoformat(), 'timeZone': 'America/New_York'},
        }

        # Add attendee if email provided
        if attendee_email:
            event['attendees'] = [{'email': attendee_email}]
            
            # Add Google Meet conference data when attendee is present
            event['conferenceData'] = {
                'createRequest': {
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                    'requestId': str(uuid.uuid4())  # Unique request ID
                }
            }

        # Insert event with conference data version if Meet link requested
        if attendee_email:
            result = service.events().insert(
                calendarId='primary', 
                body=event, 
                conferenceDataVersion=1
            ).execute()
        else:
            result = service.events().insert(calendarId='primary', body=event).execute()

        # Build response message
        event_time = start.strftime('%A, %B %d at %I:%M %p')
        response = f" Event created: '{summary}' on {event_time}"
        
        # Add attendee info if present
        if attendee_email:
            response += f"\n Attendee invited: {attendee_email}"
        
        # Add Google Meet link if available
        meet_link = result.get('hangoutLink')
        if meet_link:
            response += f"\n Google Meet: {meet_link}"
        else:
            response += f"\n Calendar Link: {result.get('htmlLink')}"

        print(f"🔴 CREATE_CALENDAR_EVENT: Success! Returning: {response}")
        return response
    except Exception as e:
        return f"Failed to create event: {str(e)}"

@function_tool
def list_upcoming_events(max_results: int = 10) -> str:
    """
    List upcoming events with their IDs for rescheduling/deletion.
    """
    if not GOOGLE_CALENDAR_AVAILABLE:
        return "Calendar functionality is currently unavailable. Please contact our team directly to check your appointments."
    
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        if not events:
            return "You have no upcoming events."

        msg = "Upcoming Events:\n"
        for i, event in enumerate(events, 1):
            title = event.get("summary", "No title")
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_id = event.get("id", "No ID")
            # Format the datetime for better readability
            try:
                if 'T' in start:
                    start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                    formatted_start = start_dt.strftime('%A, %B %d at %I:%M %p')
                else:
                    formatted_start = start
            except:
                formatted_start = start
            
            msg += f"{i}. **{title}**\n"
            msg += f"   {formatted_start}\n"
            msg += f"   Event ID: {event_id}\n\n"

        return msg
    except Exception as e:
        return f"Failed to list events: {str(e)}"

@function_tool
def delete_event(event_id: str) -> str:
    """
    Delete a calendar event by ID.
    """
    try:
        service = get_calendar_service()
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return f"🗑️ Event with ID '{event_id}' has been deleted."
    except Exception as e:
        return f"Failed to delete event: {str(e)}"

def find_event_by_title(title: str) -> str:
    """
    Helper function to find event ID by title/summary.
    """
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        # Look for events with matching title (case-insensitive)
        for event in events:
            event_title = event.get("summary", "").lower()
            if title.lower() in event_title:
                return event.get("id", "")
        
        return ""
    except Exception as e:
        return ""

@function_tool
def reschedule_event(event_id: str, new_start_datetime: str, duration_minutes: int = 60) -> str:
    """
    Reschedule an existing calendar event.
    """
    try:
        service = get_calendar_service()
        event = service.events().get(calendarId='primary', eventId=event_id).execute()

        new_start = datetime.datetime.fromisoformat(new_start_datetime)
        new_end = new_start + datetime.timedelta(minutes=duration_minutes)

        event['start'] = {'dateTime': new_start.isoformat(), 'timeZone': 'America/New_York'}
        event['end'] = {'dateTime': new_end.isoformat(), 'timeZone': 'America/New_York'}

        updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()

        return f" Event '{event['summary']}' has been rescheduled to {new_start.strftime('%A, %B %d at %I:%M %p')}."
    except Exception as e:
        return f"Failed to reschedule event: {str(e)}"

@function_tool
def reschedule_event_by_title(title: str, new_start_datetime: str, duration_minutes: int = 60) -> str:
    """
    Reschedule an existing calendar event by searching for its title.
    """
    try:
        # Find the event by title
        event_id = find_event_by_title(title)
        if not event_id:
            return f"Could not find an event with title containing '{title}'. Please check your event list."
        
        # Use the existing reschedule function
        return reschedule_event(event_id, new_start_datetime, duration_minutes)
    except Exception as e:
        return f"Failed to reschedule event: {str(e)}"

@function_tool
def delete_event_by_title(title: str) -> str:
    """
    Delete a calendar event by searching for its title.
    """
    try:
        # Find the event by title
        event_id = find_event_by_title(title)
        if not event_id:
            return f"Could not find an event with title containing '{title}'. Please check your event list."
        
        # Get event details for confirmation
        service = get_calendar_service()
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        event_title = event.get('summary', 'Unknown')
        
        # Delete the event
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return f" Event '{event_title}' has been deleted."
    except Exception as e:
        return f"Failed to delete event: {str(e)}"