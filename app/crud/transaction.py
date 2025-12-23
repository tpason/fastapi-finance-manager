from sqlalchemy.orm import Session, selectinload, joinedload
from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionGroupedResponse,
    TransactionTimeframeGroup,
    TransactionDayGroup,
    TransactionCategoryGroup,
    TransactionGroupItem,
    TransactionCategorySummary,
    TransactionPeriodSummary,
)
from app.core.pagination import paginate_with_cursor
from app.core.date_utils import parse_date_range, get_start_of_day, get_end_of_day
from typing import Optional, List, Tuple, Dict
from datetime import datetime, timedelta, timezone as dt_timezone
from decimal import Decimal, ROUND_FLOOR
from uuid import UUID


TIMEFRAME_ORDER = ["today", "yesterday", "this_week", "this_month", "this_year"]
TIMEFRAME_SET = set(TIMEFRAME_ORDER)


def get_transaction(
    db: Session, 
    transaction_id: UUID, 
    user_id: UUID,
    load_category: bool = False,
    load_user: bool = False
) -> Optional[Transaction]:
    """
    Get transaction by ID for a specific user.
    
    Args:
        load_category: If True, eager load category relationship (prevents N+1)
        load_user: If True, eager load user relationship (prevents N+1)
    """
    query = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == user_id
    )
    
    # Eager load relationships to prevent N+1 queries
    if load_category:
        query = query.options(joinedload(Transaction.category))
    if load_user:
        query = query.options(joinedload(Transaction.user))
    
    return query.first()


def get_transactions(
    db: Session,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    type: Optional[str] = None,
    category_id: Optional[UUID] = None,
    load_category: bool = False
) -> List[Transaction]:
    """
    Get all transactions for a user with filters (offset-based pagination).
    DEPRECATED: Use get_transactions_cursor for better performance.
    
    Args:
        load_category: If True, eager load category relationship for all transactions (prevents N+1)
    """
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if type:
        query = query.filter(Transaction.type == type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    
    # Eager load category to prevent N+1 queries when accessing transaction.category
    if load_category:
        query = query.options(selectinload(Transaction.category))
    
    return query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()


def get_transactions_cursor(
    db: Session,
    user_id: UUID,
    limit: int = 20,
    cursor: Optional[UUID] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    type: Optional[str] = None,
    category_id: Optional[UUID] = None,
    load_category: bool = False,
    normalize_dates: bool = True
) -> Tuple[List[Transaction], Optional[UUID], bool]:
    """
    Get transactions for a user with cursor-based pagination.
    
    Cursor pagination works correctly with date filters because:
    1. Date filters are applied BEFORE cursor filter
    2. Composite ordering (date DESC, id DESC) ensures consistent pagination
    3. UUID7 is time-ordered, so cursor maintains correct order within date range
    
    Args:
        limit: Number of items per page (default: 20, max: 100)
        cursor: UUID7 cursor from previous page (None for first page)
        start_date: Filter by start date (will be normalized to start of day if normalize_dates=True)
        end_date: Filter by end date (will be normalized to end of day if normalize_dates=True)
        type: Filter by transaction type ('income' or 'expense')
        category_id: Filter by category ID
        load_category: If True, eager load category relationship (prevents N+1)
        normalize_dates: If True, normalize start_date to start of day and end_date to end of day
    
    Returns:
        Tuple of (items, next_cursor, has_next)
    """
    query = db.query(Transaction).filter(Transaction.user_id == user_id)
    
    # Normalize date range if requested
    if normalize_dates:
        start_date, end_date = parse_date_range(
            start_date=start_date,
            end_date=end_date,
            start_of_day=True,
            end_of_day=True
        )
    
    # Apply date filters (BEFORE cursor filter to ensure correct pagination)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    
    # Apply other filters
    if type:
        query = query.filter(Transaction.type == type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    
    # Eager load category to prevent N+1 queries
    if load_category:
        query = query.options(selectinload(Transaction.category))
    
    # Use cursor-based pagination with composite ordering
    # Order by date DESC first, then id DESC for consistent pagination with date filters
    return paginate_with_cursor(
        query=query,
        cursor_column=Transaction.id,
        limit=limit,
        cursor=cursor,
        order_desc=True,  # Newest first
        secondary_order_column=Transaction.date  # Composite ordering for date filters
    )


def get_transactions_for_grouping(
    db: Session,
    user_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    type: Optional[str] = None,
    category_id: Optional[UUID] = None,
    normalize_dates: bool = True
) -> List[Transaction]:
    """
    Get all transactions for summary/grouped reporting.
    """
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    if normalize_dates:
        start_date, end_date = parse_date_range(
            start_date=start_date,
            end_date=end_date,
            start_of_day=True,
            end_of_day=True,
        )

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if type:
        query = query.filter(Transaction.type == type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    return query.options(selectinload(Transaction.category)).order_by(Transaction.date.desc()).all()


def _ensure_timezone(dt: Optional[datetime]) -> Optional[datetime]:
    """Ensure a datetime is timezone-aware (defaults to UTC)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=dt_timezone.utc)
    return dt


def _get_next_month_start(dt: datetime) -> datetime:
    """Get the first day of the next month preserving timezone."""
    if dt.month == 12:
        return dt.replace(year=dt.year + 1, month=1, day=1)
    return dt.replace(month=dt.month + 1, day=1)


def _get_timeframe_range(timeframe: str, now: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """
    Resolve timeframe keyword into an explicit start/end datetime range.

    All datetimes are timezone-aware (UTC if naive).
    """
    normalized_now = _ensure_timezone(now or datetime.now(dt_timezone.utc))
    today_start = get_start_of_day(normalized_now)

    if timeframe == "today":
        return today_start, get_end_of_day(normalized_now)
    if timeframe == "yesterday":
        day = today_start - timedelta(days=1)
        return day, get_end_of_day(day)
    if timeframe == "this_week":
        week_start = today_start - timedelta(days=today_start.weekday())
        week_end = get_end_of_day(week_start + timedelta(days=6))
        return week_start, week_end
    if timeframe == "this_month":
        month_start = today_start.replace(day=1)
        next_month_start = _get_next_month_start(month_start)
        month_end = get_end_of_day(next_month_start - timedelta(days=1))
        return month_start, month_end
    if timeframe == "this_year":
        year_start = today_start.replace(month=1, day=1)
        year_end = get_end_of_day(year_start.replace(year=year_start.year + 1) - timedelta(days=1))
        return year_start, year_end

    raise ValueError(f"Unsupported timeframe: {timeframe}")


def _get_timeframe_anchors(now: datetime) -> Dict[str, datetime]:
    """Compute anchor datetimes for timeframe buckets."""
    now = _ensure_timezone(now)
    today_start = get_start_of_day(now)
    return {
        "today_start": today_start,
        "yesterday_start": today_start - timedelta(days=1),
        "week_start": today_start - timedelta(days=today_start.weekday()),
        "month_start": today_start.replace(day=1),
        "year_start": today_start.replace(month=1, day=1),
    }


def _get_timeframe_label(tx_date: datetime, anchors: Dict[str, datetime]) -> Optional[str]:
    """Determine which timeframe bucket a transaction belongs to."""
    tx_date = _ensure_timezone(tx_date)
    if tx_date >= anchors["today_start"]:
        return "today"
    if tx_date >= anchors["yesterday_start"]:
        return "yesterday"
    if tx_date >= anchors["week_start"]:
        return "this_week"
    if tx_date >= anchors["month_start"]:
        return "this_month"
    if tx_date >= anchors["year_start"]:
        return "this_year"
    return None


def _max_datetime(current: Optional[datetime], candidate: Optional[datetime]) -> Optional[datetime]:
    """Return the later of two datetimes (handles None)."""
    candidate = _ensure_timezone(candidate)
    current = _ensure_timezone(current)
    if candidate is None:
        return current
    if current is None or candidate > current:
        return candidate
    return current


def _allocate_percentages(raw_percents: List[Decimal]) -> List[int]:
    """
    Round percentages so they sum to 100 using largest-remainder method.
    """
    if not raw_percents:
        return []

    rounded = [int(p.to_integral_value(rounding=ROUND_FLOOR)) for p in raw_percents]
    fractions = [p - Decimal(r) for p, r in zip(raw_percents, rounded)]
    remaining = 100 - sum(rounded)

    # Ensure any non-zero raw percent that floored to 0 can get at least 1 if budget allows
    zero_nonzero = [i for i, (r, raw) in enumerate(zip(rounded, raw_percents)) if r == 0 and raw > 0]
    give_min = min(remaining, len(zero_nonzero)) if remaining > 0 else 0
    for idx in zero_nonzero[:give_min]:
        rounded[idx] += 1
        fractions[idx] = Decimal("0")  # mark as already boosted
        remaining -= 1

    if remaining > 0:
        order = sorted(range(len(raw_percents)), key=lambda i: fractions[i], reverse=True)
        for idx in order[:remaining]:
            rounded[idx] += 1
    elif remaining < 0:
        order = sorted(range(len(raw_percents)), key=lambda i: fractions[i])
        for idx in order[: abs(remaining)]:
            if rounded[idx] > 0:
                rounded[idx] -= 1

    return rounded


def _get_last_update(ts: Transaction) -> Optional[datetime]:
    """Get last modification time for a transaction."""
    return ts.updated_at or ts.created_at


def _build_timeframe_group(label: str, transactions: List[Transaction]) -> TransactionTimeframeGroup:
    """
    Build a TransactionTimeframeGroup with nested day and category aggregates.
    """
    day_buckets: Dict = {}
    for tx in transactions:
        day_key = _ensure_timezone(tx.date).date()
        day_buckets.setdefault(day_key, []).append(tx)

    day_groups: List[TransactionDayGroup] = []
    timeframe_total = Decimal("0")
    timeframe_last_update: Optional[datetime] = None

    # Sort days newest first
    for day_key, day_transactions in sorted(day_buckets.items(), key=lambda item: item[0], reverse=True):
        category_buckets: Dict = {}
        for tx in day_transactions:
            category_buckets.setdefault(tx.category_id, []).append(tx)

        category_groups: List[TransactionCategoryGroup] = []
        day_total = Decimal("0")

        for category_id, category_transactions in category_buckets.items():
            # Sort transactions in category newest first
            sorted_transactions = sorted(
                category_transactions,
                key=lambda tx: _ensure_timezone(tx.date),
                reverse=True,
            )

            cat_total = sum((tx.amount for tx in sorted_transactions), Decimal("0"))
            category_name = sorted_transactions[0].category.name if sorted_transactions[0].category else None

            category_groups.append(
                TransactionCategoryGroup(
                    category_id=category_id,
                    category_name=category_name,
                    total=cat_total,
                    transactions=[
                        TransactionGroupItem(
                            id=tx.id,
                            amount=tx.amount,
                            name=tx.name,
                            type=tx.type,
                            description=tx.description,
                            date=_ensure_timezone(tx.date),
                            category_id=tx.category_id,
                            category_name=tx.category.name if tx.category else None,
                            created_at=_ensure_timezone(tx.created_at) or _ensure_timezone(tx.date),
                            updated_at=_ensure_timezone(tx.updated_at),
                        )
                        for tx in sorted_transactions
                    ],
                )
            )

            day_total += cat_total
            for tx in sorted_transactions:
                timeframe_last_update = _max_datetime(
                    timeframe_last_update, _get_last_update(tx)
                )

        # Sort categories by total descending to show most significant first
        category_groups.sort(key=lambda group: group.total, reverse=True)

        day_groups.append(
            TransactionDayGroup(
                date=day_key,
                total=day_total,
                categories=category_groups,
            )
        )
        timeframe_total += day_total

    return TransactionTimeframeGroup(
        label=label,
        total=timeframe_total,
        lasted_update_at=timeframe_last_update,
        days=day_groups,
    )


def get_grouped_transactions(
    db: Session,
    user_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    type: Optional[str] = None,
    category_id: Optional[UUID] = None,
) -> TransactionGroupedResponse:
    """
    Return transactions grouped by timeframe/day/category with totals.
    """
    transactions = get_transactions_for_grouping(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        type=type,
        category_id=category_id,
        normalize_dates=True,
    )

    anchors = _get_timeframe_anchors(datetime.now(dt_timezone.utc))
    bucketed: Dict[str, List[Transaction]] = {label: [] for label in TIMEFRAME_ORDER}

    for tx in transactions:
        label = _get_timeframe_label(tx.date, anchors)
        if label:
            bucketed[label].append(tx)

    total = Decimal("0")
    last_update: Optional[datetime] = None

    for label in TIMEFRAME_ORDER:
        txs = bucketed.get(label, [])
        if not txs:
            continue
        group = _build_timeframe_group(label, txs)
        total += group.total
        last_update = _max_datetime(last_update, group.lasted_update_at)

    return TransactionGroupedResponse(
        total=total,
        lasted_update_at=last_update,
    )


def get_transaction_period_summary(
    db: Session,
    user_id: UUID,
    timeframe: str,
    now: Optional[datetime] = None,
) -> TransactionPeriodSummary:
    """
    Return totals and category breakdown for a specific timeframe keyword.
    """
    normalized_timeframe = (timeframe or "").lower()
    if normalized_timeframe not in TIMEFRAME_SET:
        raise ValueError(f"Invalid timeframe '{timeframe}'. Expected one of {', '.join(TIMEFRAME_ORDER)}")

    start_date, end_date = _get_timeframe_range(normalized_timeframe, now=now)
    transactions = get_transactions_for_grouping(
        db=db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        normalize_dates=False,
    )

    total_income = Decimal("0")
    total_expense = Decimal("0")
    category_totals: Dict[str, Dict[Optional[UUID], Dict[str, object]]] = {
        "income": {},
        "expense": {},
    }

    for tx in transactions:
        amount = Decimal(tx.amount)
        if tx.type == "income":
            total_income += amount
        elif tx.type == "expense":
            total_expense += amount
        else:
            continue  # Skip unknown types defensively

        bucket = category_totals[tx.type].setdefault(
            tx.category_id,
            {
                "total": Decimal("0"),
                "name": tx.category.name if tx.category else None,
                "color": tx.category.color if tx.category else None,
                "icon": tx.category.icon if tx.category else None,
            },
        )
        bucket["total"] += amount

    combined_total = total_income + total_expense
    raw_rows: List[Dict] = []
    for tx_type, bucket in category_totals.items():
        for category_id, data in bucket.items():
            raw_percent = (
                (data["total"] / combined_total) * Decimal("100")
                if combined_total > 0
                else Decimal("0")
            )
            raw_rows.append(
                {
                    "category_id": category_id,
                    "category_name": data["name"],
                    "type": tx_type,
                    "total": data["total"],
                    "color": data["color"],
                    "icon": data["icon"],
                    "raw_percent": raw_percent,
                }
            )

    allocated_percents = _allocate_percentages([row["raw_percent"] for row in raw_rows])
    category_summaries: List[TransactionCategorySummary] = []
    for row, pct in zip(raw_rows, allocated_percents):
        category_summaries.append(
            TransactionCategorySummary(
                category_id=row["category_id"],
                category_name=row["category_name"],
                type=row["type"],
                total=row["total"],
                percentage=pct,
                color=row["color"],
                icon=row["icon"],
            )
        )

    type_rank = {"expense": 0, "income": 1}
    category_summaries.sort(key=lambda item: item.total, reverse=True)
    category_summaries.sort(key=lambda item: type_rank.get(item.type, 2))

    return TransactionPeriodSummary(
        timeframe=normalized_timeframe,
        start_date=start_date,
        end_date=end_date,
        total_income=total_income,
        total_expense=total_expense,
        net=total_income - total_expense,
        categories=category_summaries,
    )


def create_transaction(db: Session, transaction: TransactionCreate, user_id: UUID) -> Transaction:
    """Create a new transaction"""
    db_transaction = Transaction(
        **transaction.model_dump(),
        user_id=user_id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def update_transaction(
    db: Session,
    transaction_id: UUID,
    transaction_update: TransactionUpdate,
    user_id: UUID
) -> Optional[Transaction]:
    """Update a transaction"""
    db_transaction = get_transaction(db, transaction_id, user_id)
    if not db_transaction:
        return None
    
    update_data = transaction_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_transaction, field, value)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def delete_transaction(db: Session, transaction_id: UUID, user_id: UUID) -> bool:
    """Delete a transaction"""
    db_transaction = get_transaction(db, transaction_id, user_id)
    if not db_transaction:
        return False
    
    db.delete(db_transaction)
    db.commit()
    return True
