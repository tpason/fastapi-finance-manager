"""
Pytest configuration and fixtures for testing.
"""
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.engine import Engine
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal

from app.core.database import Base, get_db
from app.core.config import settings
from app.main import app
from app.models import User, Transaction, Category, UserDeviceToken, UserCategory
from app.crud import user as crud_user
from app.models.enums import CategoryType
from app.schemas.user import UserCreate


# Test database URL
# For PostgreSQL (recommended): Set TEST_DATABASE_URL environment variable
# Example: export TEST_DATABASE_URL="postgresql://user:pass@localhost/test_db"
# For SQLite (simpler but UUID support is limited): Use default
from app.core.config import settings

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL:
    # Try to use PostgreSQL test database if main DB is PostgreSQL
    if settings.DATABASE_URL and settings.DATABASE_URL.startswith("postgresql"):
        # Create test database URL from main database URL
        main_db_url = settings.DATABASE_URL
        if "/" in main_db_url:
            base_url = main_db_url.rsplit("/", 1)[0]
            TEST_DATABASE_URL = f"{base_url}/test_financial_management"
        else:
            TEST_DATABASE_URL = "sqlite:///:memory:"
    else:
        TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
if TEST_DATABASE_URL.startswith("sqlite"):
    # SQLite setup
    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    # Enable foreign keys for SQLite
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # PostgreSQL setup (full UUID support)
    test_engine = create_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
    )

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    """
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client with database override.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """
    Create a test user.
    """
    user_data = UserCreate(
        email="test@example.com",
        username="testuser",
        password="testpassword123",
        full_name="Test User"
    )
    user = crud_user.create_user(db_session, user_data)
    return user


@pytest.fixture
def test_user2(db_session):
    """
    Create a second test user.
    """
    user_data = UserCreate(
        email="test2@example.com",
        username="testuser2",
        password="testpassword123",
        full_name="Test User 2"
    )
    user = crud_user.create_user(db_session, user_data)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """
    Get authentication headers for test_user.
    """
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers_user2(client, test_user2):
    """
    Get authentication headers for test_user2.
    """
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser2", "password": "testpassword123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_category(db_session, test_user):
    """
    Create a test category.
    """
    category = Category(
        name="Food",
        description="Food expenses",
        type=CategoryType.EXPENSE,
        color="#FF5733",
        icon="food",
    )
    db_session.add(category)
    db_session.add(UserCategory(user_id=test_user.id, category=category))
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_transactions(db_session, test_user, test_category):
    """
    Create multiple test transactions.
    """
    transactions = []
    base_date = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    
    for i in range(10):
        transaction = Transaction(
            amount=Decimal(f"{100 + i * 10}.00"),
            type="expense" if i % 2 == 0 else "income",
            description=f"Test transaction {i+1}",
            date=base_date.replace(day=15 + i),
            user_id=test_user.id,
            category_id=test_category.id if i % 2 == 0 else None
        )
        db_session.add(transaction)
        transactions.append(transaction)
    
    db_session.commit()
    for transaction in transactions:
        db_session.refresh(transaction)
    
    return transactions
