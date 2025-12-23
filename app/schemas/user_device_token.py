from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserDeviceTokenBase(BaseModel):
    device_token: str
    device_id: str
    device_name: Optional[str] = None
    device_type: str  # 'ios', 'android', 'web', etc.


class UserDeviceTokenCreate(UserDeviceTokenBase):
    pass


class UserDeviceTokenUpdate(BaseModel):
    device_token: Optional[str] = None
    device_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserDeviceToken(UserDeviceTokenBase):
    id: UUID
    user_id: UUID
    is_active: bool
    last_used_at: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

