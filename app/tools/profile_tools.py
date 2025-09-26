from typing import Optional, Dict, Any
from agents import function_tool

PROFILE_KEY = "profile"
APPT_KEY = "appointment"

def _ensure_profile(session) -> Dict[str, Any]:
    prof = session.get(PROFILE_KEY) or {}
    if not isinstance(prof, dict):
        prof = {}
    for k in ["name", "phone", "email", "location", "age", "gender", "tz"]:
        prof.setdefault(k, None)
    session.set(PROFILE_KEY, prof)
    return prof

@function_tool
async def profile_set(session: Any,
                      name: Optional[str] = None,
                      phone: Optional[str] = None,
                      email: Optional[str] = None,
                      location: Optional[str] = None,
                      age: Optional[str] = None,
                      gender: Optional[str] = None,
                      tz: Optional[str] = None) -> str:
    """Persist user profile fields into the current session."""
    prof = _ensure_profile(session)
    updates = {"name": name, "phone": phone, "email": email, "location": location, "age": age, "gender": gender, "tz": tz}
    for k, v in updates.items():
        if v is not None:
            prof[k] = v
    session.set(PROFILE_KEY, prof)
    return "Saved."

@function_tool
async def profile_get(field: str, session: Any) -> str:
    """Return a single field from profile or a helpful fallback."""
    prof = _ensure_profile(session)
    val = prof.get(field.lower())
    return val if val else f"(no {field} on file)"

@function_tool
async def appointment_set(iso_start: str,
                          iso_end: Optional[str] = None,
                          tz: Optional[str] = "Europe/Istanbul",
                          meet_link: Optional[str] = None,
                          notes: Optional[str] = None,
                          session: Any = None) -> str:
    """Save the confirmed appointment to session."""
    session.set(APPT_KEY, {"iso_start": iso_start, "iso_end": iso_end, "tz": tz, "meet_link": meet_link, "notes": notes})
    return "Appointment saved."

@function_tool
async def appointment_get(session: Any) -> str:
    """Return a friendly one-liner about the saved appointment, if any."""
    appt = session.get(APPT_KEY)
    if not appt:
        return "(no appointment on file)"
    s = appt.get("iso_start") or ""
    e = appt.get("iso_end") or ""
    tz = appt.get("tz") or "Europe/Istanbul"
    link = appt.get("meet_link") or ""
    return f"{s}{'–'+e if e else ''} ({tz}){(' • ' + link) if link else ''}"

def sanitize_outbound(text: str) -> str:
    """Clean up WhatsApp artifacts and junk text."""
    junk = ["‎Read more", "Read more", "\u200e", "‎", "…Read more"]
    for j in junk:
        text = text.replace(j, "")
    return text.strip()
