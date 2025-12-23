from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.core.database import get_db
from app.crud import category as crud_category
from app.schemas.category import (
    Category, 
    CategoryCreate, 
    CategoryUpdate,
    PaginatedCategories
)
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import User
from app.models.enums import CategoryType

router = APIRouter()


@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new category"""
    return crud_category.create_category(
        db=db, category=category, user_id=current_user.id
    )


@router.get("/", response_model=PaginatedCategories)
def read_categories(
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    cursor: Optional[UUID] = Query(None, description="UUID7 cursor from previous page"),
    type: Optional[CategoryType] = Query(None, description="Filter by category type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get categories (global and user-specific) with cursor-based pagination.
    
    - First page: Don't provide cursor
    - Next page: Use next_cursor from previous response
    """
    items, next_cursor, has_next = crud_category.get_categories_cursor(
        db=db,
        user_id=current_user.id,
        type=type,
        limit=limit,
        cursor=cursor
    )
    
    return PaginatedCategories(
        items=items,
        next_cursor=next_cursor,
        has_next=has_next,
        limit=limit
    )


@router.get("/{category_id}", response_model=Category)
def read_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get category by ID"""
    db_category = crud_category.get_category(
        db, category_id=category_id, user_id=current_user.id
    )
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return db_category


@router.put("/{category_id}", response_model=Category)
def update_category(
    category_id: UUID,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a category"""
    db_category = crud_category.update_category(
        db, category_id=category_id, category_update=category_update, user_id=current_user.id
    )
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a category"""
    success = crud_category.delete_category(
        db, category_id=category_id, user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return None
