from sqlalchemy import Column, Numeric, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.uuid7 import uuid7
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(
        String,
        nullable=False,
        default=UserRole.MEMBER.value,
        server_default=UserRole.MEMBER.value,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    limit_amount = Column(
        Numeric(10, 2),
        nullable=False,
        default=2000000.0,
        server_default="2000000.0",
    )

    # Relationships
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    user_categories = relationship(
        "UserCategory",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    categories = relationship(
        "Category",
        secondary="user_categories",
        back_populates="users",
        overlaps="user_categories",
    )
