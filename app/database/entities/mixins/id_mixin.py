import uuid
import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column


class IdMixin(MappedAsDataclass):
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default_factory=uuid.uuid4,
        init=False,
        sort_order=-1,  # Defaults to 0, so setting to -1 makes it the first column
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), init=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), init=False
    )
    deleted: Mapped[bool] = mapped_column(init=False)
