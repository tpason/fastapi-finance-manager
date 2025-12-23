"""
Tests for device token endpoints.
"""
import pytest
from fastapi import status


def test_register_device_token(client, auth_headers):
    """Test registering a device token"""
    response = client.post(
        "/api/v1/device-tokens/",
        headers=auth_headers,
        json={
            "device_token": "fcm_token_12345",
            "device_id": "device_unique_id_123",
            "device_name": "iPhone 13",
            "device_type": "ios"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["device_token"] == "fcm_token_12345"
    assert data["device_id"] == "device_unique_id_123"
    assert data["device_type"] == "ios"
    assert data["is_active"] is True


def test_register_device_token_update_existing(client, auth_headers):
    """Test registering same device_id updates existing token"""
    # First registration
    response1 = client.post(
        "/api/v1/device-tokens/",
        headers=auth_headers,
        json={
            "device_token": "fcm_token_old",
            "device_id": "same_device_id",
            "device_type": "ios"
        }
    )
    assert response1.status_code == status.HTTP_201_CREATED
    device_id = response1.json()["id"]
    
    # Second registration with same device_id
    response2 = client.post(
        "/api/v1/device-tokens/",
        headers=auth_headers,
        json={
            "device_token": "fcm_token_new",
            "device_id": "same_device_id",
            "device_type": "ios"
        }
    )
    assert response2.status_code == status.HTTP_201_CREATED
    data2 = response2.json()
    
    # Should update existing token, not create new one
    assert data2["id"] == device_id
    assert data2["device_token"] == "fcm_token_new"


def test_get_device_tokens(client, auth_headers):
    """Test getting all device tokens"""
    # Register a token first
    client.post(
        "/api/v1/device-tokens/",
        headers=auth_headers,
        json={
            "device_token": "token1",
            "device_id": "device1",
            "device_type": "ios"
        }
    )
    
    response = client.get(
        "/api/v1/device-tokens/",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_device_tokens_active_only(client, auth_headers):
    """Test getting only active device tokens"""
    # Register active token
    client.post(
        "/api/v1/device-tokens/",
        headers=auth_headers,
        json={
            "device_token": "active_token",
            "device_id": "active_device",
            "device_type": "ios"
        }
    )
    
    response = client.get(
        "/api/v1/device-tokens/",
        headers=auth_headers,
        params={"active_only": True}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    for token in data:
        assert token["is_active"] is True


def test_deactivate_device_token(client, auth_headers):
    """Test deactivating a device token"""
    # Register token
    response = client.post(
        "/api/v1/device-tokens/",
        headers=auth_headers,
        json={
            "device_token": "token_to_deactivate",
            "device_id": "device_to_deactivate",
            "device_type": "ios"
        }
    )
    token_id = response.json()["id"]
    
    # Deactivate
    response = client.post(
        f"/api/v1/device-tokens/{token_id}/deactivate",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_active"] is False


def test_delete_device_token(client, auth_headers):
    """Test deleting a device token"""
    # Register token
    response = client.post(
        "/api/v1/device-tokens/",
        headers=auth_headers,
        json={
            "device_token": "token_to_delete",
            "device_id": "device_to_delete",
            "device_type": "ios"
        }
    )
    token_id = response.json()["id"]
    
    # Delete
    response = client.delete(
        f"/api/v1/device-tokens/{token_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify deleted
    response = client.get(
        f"/api/v1/device-tokens/{token_id}",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

