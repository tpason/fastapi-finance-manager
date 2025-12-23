"""
Shared enumerations for ORM models.
"""
from enum import Enum


class UserRole(str, Enum):
    """Application roles."""

    MEMBER = "MEMBER"
    ADMIN = "ADMIN"


class CategoryType(str, Enum):
    """Category types."""

    EXPENSE = "expense"
    INCOME = "income"

