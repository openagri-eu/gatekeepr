from enum import Enum as PyEnum
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, Enum, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.sql import func
from app.database import Base


# Define Status Enum for Choices
class BaseModelStatus(PyEnum):
    INACTIVE = 0
    ACTIVE = 1
    DELETED = 2


class BaseModel(Base):
    __abstract__ = True  # Makes this an abstract base class

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, unique=True, nullable=False)
    status = Column(Enum(BaseModelStatus), default=BaseModelStatus.ACTIVE, nullable=False)

    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @declared_attr
    def __tablename__(cls):
        # Generate table name dynamically if desired
        return cls.__name__.lower()

    def soft_delete(self):
        """Soft delete by setting status to DELETED and updating deleted_at timestamp."""
        self.status = BaseModelStatus.DELETED
        self.deleted_at = datetime.now(timezone.utc)
