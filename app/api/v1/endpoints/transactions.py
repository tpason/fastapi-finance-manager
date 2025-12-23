from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.core.database import get_db
from app.crud import transaction as crud_transaction
from app.schemas.transaction import (
    Transaction, 
    TransactionCreate, 
    TransactionUpdate,
    PaginatedTransactions,
    TransactionGroupedResponse,
    TransactionPeriodSummary,
)
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import User

router = APIRouter()


@router.post("/", response_model=Transaction, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new transaction"""
    return crud_transaction.create_transaction(
        db=db, transaction=transaction, user_id=current_user.id
    )


@router.get("/", response_model=PaginatedTransactions)
def read_transactions(
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    cursor: Optional[UUID] = Query(None, description="UUID7 cursor from previous page"),
    start_date: Optional[datetime] = Query(
        None, 
        description="Filter by start date (will be normalized to start of day: 00:00:00)"
    ),
    end_date: Optional[datetime] = Query(
        None, 
        description="Filter by end date (will be normalized to end of day: 23:59:59)"
    ),
    type: Optional[str] = Query(
        None, 
        regex="^(income|expense)$",
        description="Filter by transaction type: 'income' or 'expense'"
    ),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get transactions for current user with cursor-based pagination.
    
    **Cursor pagination works correctly with all filters including date ranges:**
    - Date filters are applied BEFORE cursor filter
    - Composite ordering (date DESC, id DESC) ensures consistent pagination
    - UUID7 is time-ordered, maintaining correct order within date range
    
    **Filters:**
    - `start_date`: Filter from this date (normalized to start of day)
    - `end_date`: Filter until this date (normalized to end of day)
    - `type`: Filter by 'income' or 'expense'
    - `category_id`: Filter by category UUID
    - `user_id`: Automatically filtered by current user
    
    **Pagination:**
    - First page: Don't provide cursor
    - Next page: Use `next_cursor` from previous response
    - Check `has_next` to know if more pages exist
    
    **Examples:**
    - Get all transactions: `GET /transactions/?limit=20`
    - Get transactions for a date range: `GET /transactions/?start_date=2024-01-01&end_date=2024-01-31`
    - Get income transactions: `GET /transactions/?type=income`
    - Get next page: `GET /transactions/?limit=20&cursor=<next_cursor_from_previous_response>`
    """
    items, next_cursor, has_next = crud_transaction.get_transactions_cursor(
        db=db,
        user_id=current_user.id,
        limit=limit,
        cursor=cursor,
        start_date=start_date,
        end_date=end_date,
        type=type,
        category_id=category_id,
        normalize_dates=True,  # Automatically normalize dates to start/end of day
        load_category=True  # Eager load category relationship
    )
    
    return PaginatedTransactions(
        items=items,
        next_cursor=next_cursor,
        has_next=has_next,
        limit=limit
    )


@router.get("/summary", response_model=TransactionGroupedResponse)
def read_transaction_summary(
    start_date: Optional[datetime] = Query(
        None,
        description="Filter by start date (normalized to start of day: 00:00:00)",
    ),
    end_date: Optional[datetime] = Query(
        None,
        description="Filter by end date (normalized to end of day: 23:59:59)",
    ),
    type: Optional[str] = Query(
        None,
        regex="^(income|expense)$",
        description="Filter by transaction type: 'income' or 'expense'",
    ),
    category_id: Optional[UUID] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get transactions grouped by timeframe (today, yesterday, this week, this month, this year).

    Each timeframe contains days, categories, and totals:
    - `total`: Sum of transaction amounts in the scope
    - `lasted_update_at`: Latest update timestamp among the transactions in the scope
    - `days`: Day buckets with category totals and transaction lists
    """
    return crud_transaction.get_grouped_transactions(
        db=db,
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        type=type,
        category_id=category_id,
    )


@router.get("/summary/timeframes/{timeframe}", response_model=TransactionPeriodSummary)
def read_transaction_period_summary(
    timeframe: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get totals and category breakdown for a timeframe keyword:
    today, yesterday, this_week, this_month, this_year.
    """
    try:
        return crud_transaction.get_transaction_period_summary(
            db=db,
            user_id=current_user.id,
            timeframe=timeframe,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )


@router.get("/{transaction_id}", response_model=Transaction)
def read_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get transaction by ID"""
    db_transaction = crud_transaction.get_transaction(
        db, transaction_id=transaction_id, user_id=current_user.id
    )
    if db_transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return db_transaction


@router.put("/{transaction_id}", response_model=Transaction)
def update_transaction(
    transaction_id: UUID,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a transaction"""
    db_transaction = crud_transaction.update_transaction(
        db, transaction_id=transaction_id, transaction_update=transaction_update, user_id=current_user.id
    )
    if db_transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return db_transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a transaction"""
    success = crud_transaction.delete_transaction(
        db, transaction_id=transaction_id, user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    return None
