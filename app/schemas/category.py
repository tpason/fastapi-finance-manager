from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID
from app.core.pagination import PaginatedResponse
from app.models.enums import CategoryType


class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: CategoryType  # 'income' or 'expense'
    color: Optional[str] = None
    icon: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[CategoryType] = None
    color: Optional[str] = None
    icon: Optional[str] = None


class Category(CategoryBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Paginated response for categories
class PaginatedCategories(PaginatedResponse[Category]):
    pass
