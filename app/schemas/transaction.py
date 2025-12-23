from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from uuid import UUID
from app.core.pagination import PaginatedResponse
from app.schemas.category import Category


class TransactionBase(BaseModel):
    amount: Decimal
    name: str
    type: str  # 'income' or 'expense'
    description: Optional[str] = None
    date: datetime
    category_id: Optional[UUID] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[Decimal] = None
    type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    category_id: Optional[UUID] = None


class Transaction(TransactionBase):
    id: UUID
    user_id: UUID
    category: Optional[Category] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Paginated response for transactions
class PaginatedTransactions(PaginatedResponse[Transaction]):
    pass


class TransactionGroupItem(BaseModel):
    id: UUID
    amount: Decimal
    type: str
    name: str
    description: Optional[str] = None
    date: datetime
    category_id: Optional[UUID] = None
    category_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TransactionCategoryGroup(BaseModel):
    category_id: Optional[UUID] = None
    category_name: Optional[str] = None
    total: Decimal
    transactions: List[TransactionGroupItem]


class TransactionDayGroup(BaseModel):
    date: date
    total: Decimal
    categories: List[TransactionCategoryGroup]


class TransactionTimeframeGroup(BaseModel):
    label: str
    total: Decimal
    lasted_update_at: Optional[datetime]
    days: List[TransactionDayGroup]


class TransactionGroupedResponse(BaseModel):
    total: Decimal
    lasted_update_at: Optional[datetime]


class TransactionCategorySummary(BaseModel):
    category_id: Optional[UUID] = None
    category_name: Optional[str] = None
    type: str  # 'income' or 'expense'
    total: Decimal
    percentage: float
    color: Optional[str] = None
    icon: Optional[str] = None


class TransactionPeriodSummary(BaseModel):
    timeframe: str
    start_date: datetime
    end_date: datetime
    total_income: Decimal
    total_expense: Decimal
    net: Decimal
    categories: List[TransactionCategorySummary]
