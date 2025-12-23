"""
Database adapter for testing with SQLite (UUID support).
"""
from sqlalchemy import TypeDecorator, String
from sqlalchemy.dialects import sqlite
from uuid import UUID as UUIDType


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    Uses PostgreSQL's UUID type when available, otherwise uses String.
    """
    impl = String
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(sqlalchemy.dialects.postgresql.UUID())
        else:
            return dialect.type_descriptor(String(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, UUIDType):
                return str(UUIDType(value))
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, UUIDType):
                return UUIDType(value)
            return value

