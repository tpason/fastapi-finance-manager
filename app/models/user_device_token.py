from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.core.uuid7 import uuid7


class UserDeviceToken(Base):
    __tablename__ = "user_device_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    device_token = Column(String, nullable=False, index=True)  # Push notification token
    device_id = Column(String, nullable=False)  # Unique device identifier
    device_name = Column(String, nullable=True)  # Device name (e.g., "iPhone 13", "Samsung Galaxy")
    device_type = Column(String, nullable=False)  # 'ios', 'android', 'web', etc.
    is_active = Column(Boolean, default=True, nullable=False)
    last_used_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user = relationship("User", backref="device_tokens")

    # Unique constraint: one token per device per user
    __table_args__ = (
        UniqueConstraint('user_id', 'device_id', name='uq_user_device'),
    )
