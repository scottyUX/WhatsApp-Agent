from typing import Dict, Any, Optional
from agents import function_tool

STATE_KEY = "questionnaire_state"

# === Questionnaire catalog ===
QUESTIONNAIRE = {
    "basic_info": {
        "label": "Basic Info",
        "questions": [
            {"id": "location",  "q": "Which city and country are you currently in?",
             "why": "Knowing your location helps us plan time zones and logistics."},
            {"id": "age",       "q": "What is your age?",
             "why": "Age helps the specialist tailor recommendations."},
            {"id": "gender",    "q": "What is your gender?",
             "why": "Gender can affect hair-loss patterns and planning."},
        ],
    },
    "medical_info": {
        "label": "Medical Info",
        "questions": [
            {"id": "conditions", "q": "Do you have any chronic illnesses or medical conditions?",
             "why": "Some conditions affect candidacy and recovery."},
            {"id": "medications","q": "Are you currently taking any medications?",
             "why": "Certain medications require special precautions."},
            {"id": "allergies",  "q": "Do you have any allergies?",
             "why": "Allergies help us avoid adverse reactions."},
            {"id": "surgeries",  "q": "Have you had any past surgeries?",
             "why": "Surgical history informs safety and planning."},
            {"id": "heart",      "q": "Any heart conditions?",
             "why": "Cardiac history can impact procedure safety."},
            {"id": "contagious", "q": "Any contagious diseases we should be aware of?",
             "why": "Important for clinical safety."},
        ],
    },
    "hair_loss": {
        "label": "Hair Loss Info",
        "questions": [
            {"id": "areas",      "q": "Where are you experiencing hair loss (e.g., hairline, crown, top)?",
             "why": "Location informs graft distribution and design."},
            {"id": "onset",      "q": "When did your hair loss start?",
             "why": "Timeline helps estimate progression."},
            {"id": "family",     "q": "Any family history of hair loss?",
             "why": "Genetics influence prognosis and planning."},
            {"id": "treatments", "q": "Have you tried any treatments (e.g., finasteride, minoxidil, PRP)?",
             "why": "Past treatments guide next steps."},
        ],
    },
}

STATE_KEY = "questionnaire_state"

def _default_state() -> Dict[str, Any]:
    # JSON-serializable only (no sets)
    return {
        "active": False,
        "category_order": ["basic_info", "medical_info", "hair_loss"],
        "cat_idx": 0,
        "q_idx": 0,
        "answers": {},          # {question_id: "value" or "skipped"}
        "skipped_cats": [],     # list[str]
    }

def _load_state(session) -> Dict[str, Any]:
    st = session.get(STATE_KEY) or {}
    if not st:
        st = _default_state()
    # defensive: ensure required keys exist
    base = _default_state()
    base.update({k: st.get(k, base[k]) for k in base.keys()})
    return base

def _save_state(session, state: Dict[str, Any]):
    session.set(STATE_KEY, state)

def _current_cat(state: Dict[str, Any]) -> Optional[str]:
    order = state["category_order"]
    return order[state["cat_idx"]] if state["cat_idx"] < len(order) else None

def _advance(state: Dict[str, Any]):
    cat = _current_cat(state)
    if cat is None:
        return
    n = len(QUESTIONNAIRE[cat]["questions"])
    state["q_idx"] += 1
    if state["q_idx"] >= n:
        state["cat_idx"] += 1
        state["q_idx"] = 0

def _summary(state: Dict[str, Any]) -> str:
    lines = []
    for cat_key in state["category_order"]:
        label = QUESTIONNAIRE[cat_key]["label"]
        lines.append(f"{label}:")
        for q in QUESTIONNAIRE[cat_key]["questions"]:
            val = state["answers"].get(q["id"], "(not provided)")
            lines.append(f"• {q['id']}: {val}")
    return "\n".join(lines)

def _echo_like(answer: str, question: str) -> bool:
    a = set(answer.lower().split())
    q = set(question.lower().split())
    return len(a & q) / max(1, len(a)) > 0.6

@function_tool
async def questionnaire_start(session) -> str:
    """
    Start the structured questionnaire; asks exactly one question at a time.
    """
    state = _default_state()
    state["active"] = True
    _save_state(session, state)

    cat = _current_cat(state)
    q = QUESTIONNAIRE[cat]["questions"][0]
    return (
        "Thanks! This short, optional questionnaire helps our specialist prepare.\n"
        "You can reply with 'skip' to skip any question, or 'skip all' to skip the entire section.\n\n"
        f"{QUESTIONNAIRE[cat]['label']} — {q['q']}\n"
        f"_Why we ask: {q['why']}_"
    )

@function_tool
async def questionnaire_answer(user_text: str, session) -> str:
    """
    Record an answer, handle skip/skip all, and return the next question or a summary.
    """
    state = _load_state(session)
    
    if not state["active"]:
        return "The questionnaire isn't active. Say 'start questionnaire' if you'd like to begin."

    t = (user_text or "").strip()
    tl = t.lower()

    # handle skip all -> jump category
    if tl in ("skip all", "skipall"):
        cat = _current_cat(state)
        if cat is not None and cat not in state["skipped_cats"]:
            state["skipped_cats"].append(cat)
        state["cat_idx"] += 1
        state["q_idx"] = 0

    # handle skip -> mark current question skipped
    elif tl in ("skip", "pass"):
        cat = _current_cat(state)
        if cat is None:
            state["active"] = False
            _save_state(session, state)
            return "All done."
        q = QUESTIONNAIRE[cat]["questions"][state["q_idx"]]
        state["answers"][q["id"]] = "skipped"
        _advance(state)

    else:
        # normal answer (with echoed-question guard)
        cat = _current_cat(state)
        if cat is None:
            state["active"] = False
            _save_state(session, state)
            return "All done."
        q = QUESTIONNAIRE[cat]["questions"][state["q_idx"]]
        if _echo_like(t, q["q"]):
            _save_state(session, state)  # no mutation yet, just to be safe
            return (
                "No worries—here are examples to guide your answer:\n"
                "• Diagnosed conditions (e.g., thyroid, anemia)\n"
                "• Medications (e.g., finasteride, minoxidil, blood thinners)\n"
                "• Prior surgeries / graft counts\n"
                "• Family history of hair loss\n"
                "• Photos: front/top/crown in good light\n\n"
                "You can reply, or say 'skip'."
            )
        state["answers"][q["id"]] = t
        _advance(state)

    # next prompt or summary
    cat = _current_cat(state)
    if cat is None:
        state["active"] = False
        _save_state(session, state)
        return "Thanks! I've noted your answers.\n\n" + _summary(state)

    q = QUESTIONNAIRE[cat]["questions"][state["q_idx"]]
    _save_state(session, state)
    return (
        f"{QUESTIONNAIRE[cat]['label']} — {q['q']}\n"
        f"_Why we ask: {q['why']}_"
    )

@function_tool
async def questionnaire_cancel(session) -> str:
    """Cancel the questionnaire gracefully."""
    state = _load_state(session)
    state["active"] = False
    _save_state(session, state)
    return "No problem—I've stopped the questionnaire. We can proceed without it."

@function_tool
async def questionnaire_status(session) -> str:
    """Check if questionnaire is active and return current state."""
    state = session.get(STATE_KEY, {})
    if not state.get("active"):
        return "inactive"
    return f"active: {state['category_order'][state['cat_idx']]} - question {state['q_idx']}"
