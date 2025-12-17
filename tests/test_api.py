"""Tests for API endpoints."""

import pytest


def test_root_redirect(client):
    """Test that root path redirects to static/index.html."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    
    # Check activity structure
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_get_activities_has_expected_fields(client):
    """Test that activities have all required fields."""
    response = client.get("/activities")
    data = response.json()
    
    for activity_name, activity_data in data.items():
        assert isinstance(activity_name, str)
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert isinstance(activity_data["max_participants"], int)
        assert "participants" in activity_data
        assert isinstance(activity_data["participants"], list)


def test_signup_new_participant(client, reset_activities):
    """Test signing up a new participant for an activity."""
    email = "test@example.com"
    activity = "Basketball Team"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity in data["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity]["participants"]


def test_signup_existing_participant(client, reset_activities):
    """Test that signing up an already registered participant fails."""
    email = "michael@mergington.edu"
    activity = "Chess Club"
    
    # Michael is already in Chess Club
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()


def test_signup_nonexistent_activity(client, reset_activities):
    """Test signing up for a non-existent activity."""
    email = "test@example.com"
    activity = "Nonexistent Activity"
    
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()


def test_unregister_participant(client, reset_activities):
    """Test unregistering a participant from an activity."""
    email = "michael@mergington.edu"
    activity = "Chess Club"
    
    # Michael is initially in Chess Club
    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity]["participants"]
    
    # Unregister
    response = client.post(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity]["participants"]


def test_unregister_nonexistent_activity(client, reset_activities):
    """Test unregistering from a non-existent activity."""
    email = "test@example.com"
    activity = "Nonexistent Activity"
    
    response = client.post(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data


def test_unregister_not_registered_participant(client, reset_activities):
    """Test unregistering a participant who isn't registered."""
    email = "notregistered@example.com"
    activity = "Chess Club"
    
    response = client.post(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not registered" in data["detail"].lower()


def test_signup_and_unregister_flow(client, reset_activities):
    """Test a complete flow of signing up and then unregistering."""
    email = "newstudent@example.com"
    activity = "Basketball Team"
    
    # Sign up
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify signed up
    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity]["participants"]
    
    # Unregister
    response = client.post(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify unregistered
    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity]["participants"]
