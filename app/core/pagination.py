"""
Cursor-based pagination utilities.
Uses UUID7 (time-ordered) as cursor for efficient pagination.
"""
from typing import Generic, TypeVar, Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Query
from sqlalchemy import Column
from pydantic import BaseModel

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters"""
    limit: int = 20
    cursor: Optional[UUID] = None  # UUID7 of the last item from previous page
    
    class Config:
        json_schema_extra = {
            "example": {
                "limit": 20,
                "cursor": "019add06-2e71-77a3-af00-40499a09182b"
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response with cursor"""
    items: List[T]
    next_cursor: Optional[UUID] = None  # UUID7 of the last item in current page
    has_next: bool = False
    limit: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "items": [],
                "next_cursor": "019add06-2e71-77a3-af00-40499a09182b",
                "has_next": True,
                "limit": 20
            }
        }


def paginate_with_cursor(
    query: Query,
    cursor_column: Column,
    limit: int = 20,
    cursor: Optional[UUID] = None,
    order_desc: bool = True,
    secondary_order_column: Optional[Column] = None
) -> Tuple[List, Optional[UUID], bool]:
    """
    Apply cursor-based pagination to a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        cursor_column: Column to use as cursor (typically the ID column)
        limit: Number of items per page (default: 20, max: 100)
        cursor: UUID7 cursor from previous page (None for first page)
        order_desc: If True, order by cursor_column DESC (default: True)
        secondary_order_column: Optional secondary column for ordering (e.g., date column)
                              Used for composite ordering when filtering by date ranges
    
    Returns:
        Tuple of (items, next_cursor, has_next)
        - items: List of results for current page
        - next_cursor: UUID7 of last item (None if no next page)
        - has_next: Boolean indicating if there are more items
    """
    # Limit max page size
    limit = min(limit, 100)
    limit = max(limit, 1)
    
    # Apply cursor filter if provided
    if cursor:
        if order_desc:
            query = query.filter(cursor_column < cursor)
        else:
            query = query.filter(cursor_column > cursor)
    
    # Order by cursor column (and secondary column if provided)
    if secondary_order_column:
        # Composite ordering: secondary column first, then cursor column
        if order_desc:
            query = query.order_by(secondary_order_column.desc(), cursor_column.desc())
        else:
            query = query.order_by(secondary_order_column.asc(), cursor_column.asc())
    else:
        # Simple ordering by cursor column only
        if order_desc:
            query = query.order_by(cursor_column.desc())
        else:
            query = query.order_by(cursor_column.asc())
    
    # Fetch limit + 1 to check if there's a next page
    items = query.limit(limit + 1).all()
    
    # Check if there's a next page
    has_next = len(items) > limit
    if has_next:
        items = items[:limit]
    
    # Get next cursor (UUID of last item)
    next_cursor = None
    if items:
        last_item = items[-1]
        # Get the cursor value - cursor_column.key gives us the attribute name
        cursor_attr_name = cursor_column.key
        next_cursor = getattr(last_item, cursor_attr_name, None)
    
    return items, next_cursor, has_next

