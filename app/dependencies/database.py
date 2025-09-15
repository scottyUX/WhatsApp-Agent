from typing import Annotated
from fastapi import Depends

from app.database.db import get_db


# Database dependency - using object type to avoid sqlalchemy import issues
DatabaseDep = Annotated[object, Depends(get_db)]
