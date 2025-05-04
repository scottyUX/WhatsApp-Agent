 # tools/collect_user_info.py
from agents import Tool
from agents import Agent, FunctionTool, RunContextWrapper, function_tool
from typing_extensions import TypedDict, Any


class UserInfo(TypedDict):
    first_name: str
    last_name: str
    email: str

@function_tool
def collect_user_info(user_info: UserInfo) -> UserInfo:
    """
    Collect basic user info. Prompt for any missing fields.
    """
    missing = []
    if not user_info["first_name"]:
        missing.append("first name")
    if not user_info["last_name"]:
        missing.append("last name")
    if not user_info["email"]:
        missing.append("email")

    if missing:
        return f"To get started, please share your {', '.join(missing)}."
    return f"Thanks {user_info['first_name']} {user_info['last_name']}. We’ve recorded your email ({user_info['email']})."
