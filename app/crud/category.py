from sqlalchemy.orm import Session, joinedload
from sqlalchemy import exists, or_
from app.models.category import Category
from app.models.user_category import UserCategory
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.core.pagination import paginate_with_cursor
from typing import Optional, List, Tuple
from uuid import UUID
from app.models.enums import CategoryType


def get_category(
    db: Session, 
    category_id: UUID, 
    user_id: Optional[UUID] = None,
    load_user: bool = False
) -> Optional[Category]:
    """
    Get category by ID.
    
    Args:
        load_user: If True, eager load user relationship (prevents N+1)
    """
    query = db.query(Category).filter(Category.id == category_id)

    if user_id:
        query = query.filter(
            or_(
                exists().where(
                    (UserCategory.category_id == Category.id) & (UserCategory.user_id == user_id)
                ),
                ~exists().where(UserCategory.category_id == Category.id),
            )
        )

    if load_user:
        query = query.options(joinedload(Category.users))
    
    return query.first()


def get_categories(
    db: Session,
    user_id: Optional[UUID] = None,
    type: Optional[CategoryType] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Category]:
    """
    Get all categories (global and user-specific) with offset-based pagination.
    DEPRECATED: Use get_categories_cursor for better performance.
    """
    query = db.query(Category)

    if user_id:
        query = query.filter(
            or_(
                exists().where(
                    (UserCategory.category_id == Category.id) & (UserCategory.user_id == user_id)
                ),
                ~exists().where(UserCategory.category_id == Category.id),
            )
        )

    if type:
        query = query.filter(Category.type == type)

    return query.offset(skip).limit(limit).all()


def get_categories_cursor(
    db: Session,
    user_id: Optional[UUID] = None,
    type: Optional[CategoryType] = None,
    limit: int = 20,
    cursor: Optional[UUID] = None,
    load_user: bool = False
) -> Tuple[List[Category], Optional[UUID], bool]:
    """
    Get categories with cursor-based pagination.
    
    Args:
        user_id: Filter by user ID (None for global categories)
        type: Filter by category type ('income' or 'expense')
        limit: Number of items per page (default: 20, max: 100)
        cursor: UUID7 cursor from previous page (None for first page)
        load_user: If True, eager load user relationship (prevents N+1)
    
    Returns:
        Tuple of (items, next_cursor, has_next)
    """
    query = db.query(Category)

    if user_id:
        query = query.filter(
            or_(
                exists().where(
                    (UserCategory.category_id == Category.id) & (UserCategory.user_id == user_id)
                ),
                ~exists().where(UserCategory.category_id == Category.id),
            )
        )

    if type:
        query = query.filter(Category.type == type)

    if load_user:
        query = query.options(joinedload(Category.users))

    # Use cursor-based pagination with UUID7
    return paginate_with_cursor(
        query=query,
        cursor_column=Category.id,
        limit=limit,
        cursor=cursor,
        order_desc=True  # Newest first
    )


def create_category(db: Session, category: CategoryCreate, user_id: Optional[UUID] = None) -> Category:
    """Create a new category"""
    db_category = Category(**category.model_dump())
    db.add(db_category)
    if user_id:
        db.add(UserCategory(user_id=user_id, category_id=db_category.id))

    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(
    db: Session,
    category_id: UUID,
    category_update: CategoryUpdate,
    user_id: Optional[UUID] = None
) -> Optional[Category]:
    """Update a category"""
    db_category = get_category(db, category_id, user_id)
    if not db_category:
        return None
    
    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: UUID, user_id: Optional[UUID] = None) -> bool:
    """Delete a category"""
    db_category = get_category(db, category_id, user_id)
    if not db_category:
        return False
    
    db.delete(db_category)
    db.commit()
    return True
