"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status


def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New User"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data
    assert data["role"] == "MEMBER"
    assert "hashed_password" not in data  # Password should not be in response


def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email"""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",  # Already exists
            "username": "differentuser",
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already registered" in response.json()["detail"].lower()


def test_register_duplicate_username(client, test_user):
    """Test registration with duplicate username"""
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "different@example.com",
            "username": "testuser",  # Already exists
            "password": "password123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "username" in response.json()["detail"].lower()


def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword123"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, test_user):
    """Test login with wrong password"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent", "password": "password123"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user(client, auth_headers):
    """Test getting current user info"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["role"] == "MEMBER"


def test_get_current_user_unauthorized(client):
    """Test getting current user without authentication"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token_success(client, test_user):
    """Test refreshing token with a valid refresh token"""
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "testpassword123"}
    )
    assert login_response.status_code == status.HTTP_200_OK
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == status.HTTP_200_OK
    data = refresh_response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
