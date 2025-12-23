from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from typing import Optional
from uuid import UUID
from app.models.enums import UserRole


def get_user(db: Session, user_id: UUID) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(or_(User.username == username, User.email == username)).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get all users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    # Guard against duplicate username/email before insert
    existing = db.query(User).filter(
        or_(User.username == user.username, User.email == user.email)
    ).first()
    if existing:
        raise ValueError("Username or email already registered")

    hashed_password = get_password_hash(user.password)
    role_value = user.role.value if isinstance(user.role, UserRole) else user.role
    user_data = {
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "hashed_password": hashed_password,
        "role": role_value or UserRole.MEMBER.value,
    }
    if user.limit_amount is not None:
        user_data["limit_amount"] = user.limit_amount
    db_user = User(**user_data)
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        # In case a concurrent insert slipped in between the pre-check and commit
        db.rollback()
        raise ValueError("Username or email already registered")
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
    """Update user information"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    if "role" in update_data and update_data["role"] is not None:
        role_value = update_data["role"]
        if isinstance(role_value, UserRole):
            role_value = role_value.value
        update_data["role"] = role_value
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: UUID) -> bool:
    """Delete a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
