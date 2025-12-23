from sqlalchemy import Column, String, DateTime, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.uuid7 import uuid7
from app.models.enums import CategoryType


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("name", "type", name="uq_category_name_type"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    type = Column(
        Enum(
            CategoryType,
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
            name="categorytype",
        ),
        nullable=False,
    )  # 'income' or 'expense'
    color = Column(String, nullable=True)  # Hex color code
    icon = Column(String, nullable=True)  # Icon name or path
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    users = relationship(
        "User",
        secondary="user_categories",
        back_populates="categories",
        overlaps="user_categories",
    )
    user_categories = relationship(
        "UserCategory",
        back_populates="category",
        cascade="all, delete-orphan",
    )
    transactions = relationship("Transaction", back_populates="category")
