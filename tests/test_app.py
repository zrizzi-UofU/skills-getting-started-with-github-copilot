"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]


def test_signup_success():
    """Test successful signup for an activity"""
    # First, get initial participants
    response = client.get("/activities")
    initial_data = response.json()
    initial_count = len(initial_data["Chess Club"]["participants"])

    # Sign up a new student
    response = client.post("/activities/Chess%20Club/signup?email=test%40mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]

    # Check that the participant was added
    response = client.get("/activities")
    updated_data = response.json()
    updated_count = len(updated_data["Chess Club"]["participants"])
    assert updated_count == initial_count + 1
    assert "test@mergington.edu" in updated_data["Chess Club"]["participants"]


def test_signup_already_signed_up():
    """Test signing up when already signed up"""
    # First sign up
    client.post("/activities/Chess%20Club/signup?email=duplicate%40mergington.edu")

    # Try to sign up again
    response = client.post("/activities/Chess%20Club/signup?email=duplicate%40mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_activity_not_found():
    """Test signing up for non-existent activity"""
    response = client.post("/activities/NonExistent/signup?email=test%40mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_success():
    """Test successful unregister from an activity"""
    # First sign up
    client.post("/activities/Programming%20Class/signup?email=unregister%40mergington.edu")

    # Get initial count
    response = client.get("/activities")
    initial_data = response.json()
    initial_count = len(initial_data["Programming Class"]["participants"])

    # Unregister
    response = client.delete("/activities/Programming%20Class/unregister?email=unregister%40mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]

    # Check that the participant was removed
    response = client.get("/activities")
    updated_data = response.json()
    updated_count = len(updated_data["Programming Class"]["participants"])
    assert updated_count == initial_count - 1
    assert "unregister@mergington.edu" not in updated_data["Programming Class"]["participants"]


def test_unregister_not_signed_up():
    """Test unregistering when not signed up"""
    response = client.delete("/activities/Chess%20Club/unregister?email=notsignedup%40mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]


def test_unregister_activity_not_found():
    """Test unregistering from non-existent activity"""
    response = client.delete("/activities/NonExistent/unregister?email=test%40mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_root_redirect():
    """Test root endpoint redirects to static index"""
    response = client.get("/")
    assert response.status_code == 200  # RedirectResponse, but TestClient follows redirects
    # Since it's a redirect to /static/index.html, and static files are mounted,
    # it should serve the HTML file