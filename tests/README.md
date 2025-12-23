# Test Suite

## Setup

1. Install test dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) Set test database URL:
```bash
export TEST_DATABASE_URL="postgresql://user:password@localhost/test_db"
```

If not set, tests will use SQLite in-memory database.

## Running Tests

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_auth.py
```

Run with verbose output:
```bash
pytest -v
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## Test Structure

- `conftest.py`: Test fixtures (database, client, test data)
- `test_auth.py`: Authentication endpoints tests
- `test_transactions.py`: Transaction endpoints with cursor pagination tests
- `test_categories.py`: Category endpoints tests
- `test_device_tokens.py`: Device token endpoints tests

## Test Coverage

Tests cover:
- ✅ User registration and authentication
- ✅ Transaction CRUD operations
- ✅ Cursor-based pagination
- ✅ Date range filtering
- ✅ Type and category filtering
- ✅ Category CRUD operations
- ✅ Device token management
- ✅ Authorization and access control

## Notes

- Tests use in-memory SQLite by default (fast, no setup needed)
- For PostgreSQL testing, set `TEST_DATABASE_URL` environment variable
- Each test gets a fresh database session
- Test fixtures create sample data automatically

