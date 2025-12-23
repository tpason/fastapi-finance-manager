"""
Tests for category endpoints.
"""
import pytest
from fastapi import status


def test_create_category(client, auth_headers):
    """Test creating a category"""
    response = client.post(
        "/api/v1/categories/",
        headers=auth_headers,
        json={
            "name": "Transportation",
            "description": "Transport expenses",
            "type": "expense",
            "color": "#3498db",
            "icon": "car"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Transportation"
    assert data["type"] == "expense"
    assert "id" in data


def test_get_categories_cursor_pagination(client, auth_headers, test_category):
    """Test getting categories with cursor pagination"""
    response = client.get(
        "/api/v1/categories/",
        headers=auth_headers,
        params={"limit": 10}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "next_cursor" in data
    assert "has_next" in data
    assert len(data["items"]) >= 1  # At least our test category


def test_get_categories_with_type_filter(client, auth_headers, test_category):
    """Test getting categories filtered by type"""
    response = client.get(
        "/api/v1/categories/",
        headers=auth_headers,
        params={"limit": 10, "type": "expense"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    # Verify all categories are expenses
    for item in data["items"]:
        assert item["type"] == "expense"


def test_get_category_by_id(client, auth_headers, test_category):
    """Test getting a specific category"""
    response = client.get(
        f"/api/v1/categories/{test_category.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(test_category.id)
    assert data["name"] == "Food"


def test_update_category(client, auth_headers, test_category):
    """Test updating a category"""
    response = client.put(
        f"/api/v1/categories/{test_category.id}",
        headers=auth_headers,
        json={
            "name": "Updated Food",
            "color": "#FF0000"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Food"
    assert data["color"] == "#FF0000"


def test_delete_category(client, auth_headers, test_category):
    """Test deleting a category"""
    response = client.delete(
        f"/api/v1/categories/{test_category.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's deleted
    response = client.get(
        f"/api/v1/categories/{test_category.id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
