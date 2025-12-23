from sqlalchemy.orm import Session
from app.models.user_device_token import UserDeviceToken
from app.schemas.user_device_token import UserDeviceTokenCreate, UserDeviceTokenUpdate
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import and_


def get_device_token(db: Session, token_id: UUID, user_id: UUID) -> Optional[UserDeviceToken]:
    """Get device token by ID for a specific user"""
    return db.query(UserDeviceToken).filter(
        and_(
            UserDeviceToken.id == token_id,
            UserDeviceToken.user_id == user_id
        )
    ).first()


def get_device_tokens_by_user(db: Session, user_id: UUID, active_only: bool = False) -> List[UserDeviceToken]:
    """Get all device tokens for a user"""
    query = db.query(UserDeviceToken).filter(UserDeviceToken.user_id == user_id)
    if active_only:
        query = query.filter(UserDeviceToken.is_active == True)
    return query.order_by(UserDeviceToken.last_used_at.desc()).all()


def get_device_token_by_device_id(db: Session, user_id: UUID, device_id: str) -> Optional[UserDeviceToken]:
    """Get device token by device_id and user_id"""
    return db.query(UserDeviceToken).filter(
        and_(
            UserDeviceToken.user_id == user_id,
            UserDeviceToken.device_id == device_id
        )
    ).first()


def create_device_token(db: Session, device_token: UserDeviceTokenCreate, user_id: UUID) -> UserDeviceToken:
    """Create a new device token"""
    db_token = UserDeviceToken(
        **device_token.model_dump(),
        user_id=user_id
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def create_or_update_device_token(
    db: Session, 
    device_token: UserDeviceTokenCreate, 
    user_id: UUID
) -> UserDeviceToken:
    """
    Create a new device token or update if device_id already exists for this user.
    This is useful for login scenarios where the same device logs in again.
    """
    existing_token = get_device_token_by_device_id(db, user_id, device_token.device_id)
    
    if existing_token:
        # Update existing token
        existing_token.device_token = device_token.device_token
        existing_token.device_name = device_token.device_name or existing_token.device_name
        existing_token.device_type = device_token.device_type
        existing_token.is_active = True
        existing_token.last_used_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(existing_token)
        return existing_token
    else:
        # Create new token
        return create_device_token(db, device_token, user_id)


def update_device_token(
    db: Session,
    token_id: UUID,
    token_update: UserDeviceTokenUpdate,
    user_id: UUID
) -> Optional[UserDeviceToken]:
    """Update a device token"""
    db_token = get_device_token(db, token_id, user_id)
    if not db_token:
        return None
    
    update_data = token_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_token, field, value)
    
    db_token.last_used_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_token)
    return db_token


def delete_device_token(db: Session, token_id: UUID, user_id: UUID) -> bool:
    """Delete a device token"""
    db_token = get_device_token(db, token_id, user_id)
    if not db_token:
        return False
    
    db.delete(db_token)
    db.commit()
    return True


def deactivate_device_token(db: Session, token_id: UUID, user_id: UUID) -> Optional[UserDeviceToken]:
    """Deactivate a device token (soft delete)"""
    db_token = get_device_token(db, token_id, user_id)
    if not db_token:
        return None
    
    db_token.is_active = False
    db.commit()
    db.refresh(db_token)
    return db_token


def update_last_used(db: Session, token_id: UUID, user_id: UUID) -> Optional[UserDeviceToken]:
    """Update last_used_at timestamp for a device token"""
    db_token = get_device_token(db, token_id, user_id)
    if not db_token:
        return None
    
    db_token.last_used_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_token)
    return db_token

