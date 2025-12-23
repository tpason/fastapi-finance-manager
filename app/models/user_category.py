from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserCategory(Base):
    __tablename__ = "user_categories"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship(
        "User",
        back_populates="user_categories",
        overlaps="categories,users",
    )
    category = relationship(
        "Category",
        back_populates="user_categories",
        overlaps="categories,users",
    )
