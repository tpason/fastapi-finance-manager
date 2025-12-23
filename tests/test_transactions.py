"""
Tests for transaction endpoints including cursor pagination.
"""
import pytest
from fastapi import status
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID


def test_create_transaction(client, auth_headers, test_category):
    """Test creating a transaction"""
    response = client.post(
        "/api/v1/transactions/",
        headers=auth_headers,
        json={
            "amount": "150.50",
            "type": "expense",
            "description": "Test transaction",
            "date": "2024-01-15T12:00:00Z",
            "category_id": str(test_category.id)
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["amount"] == "150.50"
    assert data["type"] == "expense"
    assert data["description"] == "Test transaction"
    assert "id" in data
    assert "user_id" in data


def test_create_transaction_unauthorized(client, test_category):
    """Test creating transaction without authentication"""
    response = client.post(
        "/api/v1/transactions/",
        json={
            "amount": "150.50",
            "type": "expense",
            "date": "2024-01-15T12:00:00Z"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_transactions_cursor_pagination_first_page(client, auth_headers, test_transactions):
    """Test cursor pagination - first page"""
    response = client.get(
        "/api/v1/transactions/",
        headers=auth_headers,
        params={"limit": 5}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "next_cursor" in data
    assert "has_next" in data
    assert "limit" in data
    assert len(data["items"]) == 5
    assert data["limit"] == 5
    assert data["has_next"] is True
    assert data["next_cursor"] is not None


def test_get_transactions_cursor_pagination_next_page(client, auth_headers, test_transactions):
    """Test cursor pagination - next page"""
    # Get first page
    response1 = client.get(
        "/api/v1/transactions/",
        headers=auth_headers,
        params={"limit": 5}
    )
    assert response1.status_code == status.HTTP_200_OK
    data1 = response1.json()
    next_cursor = data1["next_cursor"]
    
    # Get next page
    response2 = client.get(
        "/api/v1/transactions/",
        headers=auth_headers,
        params={"limit": 5, "cursor": next_cursor}
    )
    assert response2.status_code == status.HTTP_200_OK
    data2 = response2.json()
    
    # Verify no overlap
    first_page_ids = {item["id"] for item in data1["items"]}
    second_page_ids = {item["id"] for item in data2["items"]}
    assert len(first_page_ids.intersection(second_page_ids)) == 0


def test_get_transactions_with_date_filter(client, auth_headers, test_transactions):
    """Test transactions with date filter"""
    start_dt = datetime(2024, 1, 15, tzinfo=timezone.utc)
    end_dt = datetime(2024, 1, 20, tzinfo=timezone.utc)
    start_date = start_dt.isoformat()
    end_date = end_dt.isoformat()
    
    response = client.get(
        "/api/v1/transactions/",
        headers=auth_headers,
        params={
            "limit": 20,
            "start_date": start_date,
            "end_date": end_date
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verify all transactions are within date range
    start_of_day = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

    for item in data["items"]:
        item_date = datetime.fromisoformat(item["date"].replace("Z", "+00:00"))
        assert start_of_day <= item_date <= end_of_day


def test_get_transactions_with_type_filter(client, auth_headers, test_transactions):
    """Test transactions with type filter"""
    response = client.get(
        "/api/v1/transactions/",
        headers=auth_headers,
        params={"limit": 20, "type": "expense"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verify all transactions are expenses
    for item in data["items"]:
        assert item["type"] == "expense"


def test_get_transactions_with_category_filter(client, auth_headers, test_transactions, test_category):
    """Test transactions with category filter"""
    response = client.get(
        "/api/v1/transactions/",
        headers=auth_headers,
        params={"limit": 20, "category_id": str(test_category.id)}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verify all transactions have the correct category
    for item in data["items"]:
        if item["category_id"]:
            assert item["category_id"] == str(test_category.id)


def test_get_transactions_cursor_with_filters(client, auth_headers, test_transactions, test_category):
    """Test cursor pagination with multiple filters"""
    start_date = datetime(2024, 1, 15, tzinfo=timezone.utc).isoformat()
    end_date = datetime(2024, 1, 25, tzinfo=timezone.utc).isoformat()
    
    # First page
    response1 = client.get(
        "/api/v1/transactions/",
        headers=auth_headers,
        params={
            "limit": 3,
            "start_date": start_date,
            "end_date": end_date,
            "type": "expense",
            "category_id": str(test_category.id)
        }
    )
    assert response1.status_code == status.HTTP_200_OK
    data1 = response1.json()
    
    if data1["has_next"]:
        # Next page with same filters
        response2 = client.get(
            "/api/v1/transactions/",
            headers=auth_headers,
            params={
                "limit": 3,
                "cursor": data1["next_cursor"],
                "start_date": start_date,
                "end_date": end_date,
                "type": "expense",
                "category_id": str(test_category.id)
            }
        )
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        
        # Verify filters still applied
        for item in data2["items"]:
            assert item["type"] == "expense"
            if item["category_id"]:
                assert item["category_id"] == str(test_category.id)


def test_get_transaction_by_id(client, auth_headers, test_transactions):
    """Test getting a specific transaction"""
    transaction_id = test_transactions[0].id
    
    response = client.get(
        f"/api/v1/transactions/{transaction_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(transaction_id)


def test_get_transaction_not_found(client, auth_headers):
    """Test getting non-existent transaction"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(
        f"/api/v1/transactions/{fake_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_transaction_other_user(client, auth_headers_user2, test_transactions):
    """Test getting transaction from another user (should not be accessible)"""
    transaction_id = test_transactions[0].id
    
    response = client.get(
        f"/api/v1/transactions/{transaction_id}",
        headers=auth_headers_user2
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_transaction(client, auth_headers, test_transactions):
    """Test updating a transaction"""
    transaction_id = test_transactions[0].id
    
    response = client.put(
        f"/api/v1/transactions/{transaction_id}",
        headers=auth_headers,
        json={
            "amount": "200.00",
            "description": "Updated description"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["amount"] == "200.00"
    assert data["description"] == "Updated description"


def test_delete_transaction(client, auth_headers, test_transactions):
    """Test deleting a transaction"""
    transaction_id = test_transactions[0].id
    
    response = client.delete(
        f"/api/v1/transactions/{transaction_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's deleted
    response = client.get(
        f"/api/v1/transactions/{transaction_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

