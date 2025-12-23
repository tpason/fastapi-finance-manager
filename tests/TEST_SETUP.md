# Test Setup Guide

## Database Setup

### Option 1: PostgreSQL (Recommended)

Tests work best with PostgreSQL because it fully supports UUID types.

1. Create a test database:
```bash
createdb test_financial_management
```

2. Set environment variable:
```bash
export TEST_DATABASE_URL="postgresql://user:password@localhost/test_financial_management"
```

3. Run migrations:
```bash
alembic upgrade head
```

### Option 2: SQLite (Simpler but Limited)

SQLite can be used but has limitations with UUID types. Tests will work but may need adjustments.

```bash
# SQLite is used by default if TEST_DATABASE_URL is not set
# No setup needed
```

## Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
```

## Test Structure

- `conftest.py`: Test fixtures and database setup
- `test_auth.py`: Authentication tests
- `test_transactions.py`: Transaction API tests with cursor pagination
- `test_categories.py`: Category API tests
- `test_device_tokens.py`: Device token API tests

## Troubleshooting

### UUID Issues with SQLite

If you see UUID-related errors with SQLite, use PostgreSQL instead:
```bash
export TEST_DATABASE_URL="postgresql://user:pass@localhost/test_db"
```

### Bcrypt Issues

If bcrypt fails, ensure it's properly installed:
```bash
pip install --upgrade bcrypt passlib[bcrypt]
```

