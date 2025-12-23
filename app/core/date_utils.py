"""
Date utility functions for filtering and pagination.
"""
from datetime import datetime, time, timedelta, timezone as dt_timezone
from typing import Optional, Tuple


def get_start_of_day(dt: datetime, timezone: Optional[str] = None) -> datetime:
    """
    Get the start of day (00:00:00) for a given datetime.
    
    Args:
        dt: Input datetime
        timezone: Optional timezone string (e.g., 'UTC'). 
                 If None and dt has no timezone, assumes UTC.
    
    Returns:
        Datetime at start of day (preserves timezone info)
    """
    # If datetime is naive (no timezone), assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=dt_timezone.utc)
    
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def get_end_of_day(dt: datetime, timezone: Optional[str] = None) -> datetime:
    """
    Get the end of day (23:59:59.999999) for a given datetime.
    
    Args:
        dt: Input datetime
        timezone: Optional timezone string (e.g., 'UTC').
                 If None and dt has no timezone, assumes UTC.
    
    Returns:
        Datetime at end of day (preserves timezone info)
    """
    # If datetime is naive (no timezone), assume UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=dt_timezone.utc)
    
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def parse_date_range(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    start_of_day: bool = True,
    end_of_day: bool = True,
    timezone: Optional[str] = None
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Parse and normalize date range for filtering.
    
    Args:
        start_date: Start date (will be set to start of day if start_of_day=True)
        end_date: End date (will be set to end of day if end_of_day=True)
        start_of_day: If True, set start_date to beginning of day
        end_of_day: If True, set end_date to end of day
        timezone: Optional timezone string
    
    Returns:
        Tuple of (normalized_start_date, normalized_end_date)
    """
    normalized_start = start_date
    normalized_end = end_date
    
    if start_date and start_of_day:
        normalized_start = get_start_of_day(start_date, timezone)
    
    if end_date and end_of_day:
        normalized_end = get_end_of_day(end_date, timezone)
    
    return normalized_start, normalized_end

