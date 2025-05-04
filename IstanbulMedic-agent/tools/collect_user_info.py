 # tools/collect_user_info.py
from agents import Tool
from agents import Agent, FunctionTool, RunContextWrapper, function_tool
from typing_extensions import TypedDict, Any


class UserInfo(TypedDict):
    first_name: str
    last_name: str
    email: str

@function_tool
def collect_user_info() -> UserInfo:
    """Collects user's first name, last name, and email address from console input."""
    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    email = input("Email: ")
    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
    }
