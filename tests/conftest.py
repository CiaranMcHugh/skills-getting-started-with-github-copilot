"""Pytest configuration and fixtures for FastAPI app tests."""

import sys
from pathlib import Path

# Add the src directory to the Python path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from fastapi.testclient import TestClient
from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test."""
    # Save original state
    original_activities = {
        k: {
            "description": v["description"],
            "schedule": v["schedule"],
            "max_participants": v["max_participants"],
            "participants": v["participants"].copy(),
        }
        for k, v in activities.items()
    }
    
    yield
    
    # Restore original state after test
    for activity_name in activities:
        activities[activity_name]["participants"] = original_activities[activity_name]["participants"].copy()
