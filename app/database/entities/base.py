from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


# MappedAsDataclass is for converting SQLAlchemy models to dataclasses for typing support
# See: https://github.com/sqlalchemy/sqlalchemy/discussions/10359
# Also: https://docs.sqlalchemy.org/en/20/orm/dataclasses.html#declarative-dataclass-mapping
class Base(MappedAsDataclass, DeclarativeBase):
    pass
