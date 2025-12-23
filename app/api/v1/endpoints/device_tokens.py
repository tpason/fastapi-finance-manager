from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.core.database import get_db
from app.crud import user_device_token as crud_device_token
from app.schemas.user_device_token import (
    UserDeviceToken,
    UserDeviceTokenCreate,
    UserDeviceTokenUpdate
)
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import User

router = APIRouter()


@router.post("/", response_model=UserDeviceToken, status_code=status.HTTP_201_CREATED)
def register_device_token(
    device_token: UserDeviceTokenCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Register or update a device token for the current user.
    If device_id already exists for this user, the token will be updated.
    """
    return crud_device_token.create_or_update_device_token(
        db=db,
        device_token=device_token,
        user_id=current_user.id
    )


@router.get("/", response_model=List[UserDeviceToken])
def get_device_tokens(
    active_only: bool = Query(False, description="Only return active tokens"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all device tokens for the current user"""
    return crud_device_token.get_device_tokens_by_user(
        db=db,
        user_id=current_user.id,
        active_only=active_only
    )


@router.get("/{token_id}", response_model=UserDeviceToken)
def get_device_token(
    token_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific device token by ID"""
    db_token = crud_device_token.get_device_token(
        db, token_id=token_id, user_id=current_user.id
    )
    if db_token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device token not found"
        )
    return db_token


@router.put("/{token_id}", response_model=UserDeviceToken)
def update_device_token(
    token_id: UUID,
    token_update: UserDeviceTokenUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a device token"""
    db_token = crud_device_token.update_device_token(
        db, token_id=token_id, token_update=token_update, user_id=current_user.id
    )
    if db_token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device token not found"
        )
    return db_token


@router.delete("/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device_token(
    token_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a device token (hard delete)"""
    success = crud_device_token.delete_device_token(
        db, token_id=token_id, user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device token not found"
        )
    return None


@router.post("/{token_id}/deactivate", response_model=UserDeviceToken)
def deactivate_device_token(
    token_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deactivate a device token (soft delete)"""
    db_token = crud_device_token.deactivate_device_token(
        db, token_id=token_id, user_id=current_user.id
    )
    if db_token is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device token not found"
        )
    return db_token

