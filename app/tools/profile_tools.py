from typing import Dict, Any, Optional
from agents import function_tool, RunContextWrapper

PROFILE_KEY = "profile"
APPT_KEY = "appointment"

def _ensure_profile(context: Dict[str, Any]) -> Dict[str, Any]:
    prof = context.get(PROFILE_KEY) or {}
    if not isinstance(prof, dict): 
        prof = {}
    # normalize keys
    for k in ["name", "phone", "email", "location", "age", "gender"]:
        prof.setdefault(k, None)
    context[PROFILE_KEY] = prof
    return prof

@function_tool
async def profile_set(wrapper: RunContextWrapper,
                      name: Optional[str] = None,
                      phone: Optional[str] = None,
                      email: Optional[str] = None,
                      location: Optional[str] = None,
                      age: Optional[str] = None,
                      gender: Optional[str] = None) -> str:
    """Persist user profile fields into the current session."""
    context = wrapper.context or {}
    prof = _ensure_profile(context)
    if name is not None: prof["name"] = name
    if phone is not None: prof["phone"] = phone
    if email is not None: prof["email"] = email
    if location is not None: prof["location"] = location
    if age is not None: prof["age"] = age
    if gender is not None: prof["gender"] = gender
    context[PROFILE_KEY] = prof
    return "Profile updated."

@function_tool
async def profile_get(wrapper: RunContextWrapper, field: str) -> str:
    """Return a single field from profile or a helpful fallback."""
    context = wrapper.context or {}
    prof = _ensure_profile(context)
    val = prof.get(field.lower())
    return val if val else f"(no {field} on file)"

@function_tool
async def appointment_set(wrapper: RunContextWrapper,
                          iso_start: str,
                          iso_end: Optional[str] = None,
                          tz: Optional[str] = None,
                          meet_link: Optional[str] = None,
                          notes: Optional[str] = None) -> str:
    """Save the confirmed appointment to session."""
    context = wrapper.context or {}
    appt = {
        "iso_start": iso_start,
        "iso_end": iso_end,
        "tz": tz or "Europe/Istanbul",
        "meet_link": meet_link,
        "notes": notes
    }
    context[APPT_KEY] = appt
    return "Appointment saved."

@function_tool
async def appointment_get(wrapper: RunContextWrapper) -> str:
    """Return a friendly one-liner about the saved appointment, if any."""
    context = wrapper.context or {}
    appt = context.get(APPT_KEY)
    if not appt:
        return "(no appointment on file)"
    s = appt.get("iso_start") or ""
    e = appt.get("iso_end") or ""
    tz = appt.get("tz") or "Europe/Istanbul"
    link = appt.get("meet_link") or ""
    return f"{s}{'–'+e if e else ''} ({tz}) {('• ' + link) if link else ''}".strip()

def sanitize_outbound(text: str) -> str:
    """Clean up WhatsApp artifacts and junk text."""
    junk = ["‎Read more", "Read more", "\u200e", "‎", "…Read more"]
    for j in junk:
        text = text.replace(j, "")
    return text.strip()
