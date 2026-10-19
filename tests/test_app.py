import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)
_original = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: restore in-memory data before each test
    activities.clear()
    activities.update(copy.deepcopy(_original))


def test_get_activities():
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_signup_adds_participant():
    # Arrange
    email = "new@mergington.edu"
    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_rejected():
    # Arrange
    email = activities["Chess Club"]["participants"][0]
    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    # Assert
    assert response.status_code == 400


def test_signup_unknown_activity():
    response = client.post("/activities/Nope/signup", params={"email": "a@b.c"})
    assert response.status_code == 404


def test_unregister_removes_participant():
    # Arrange
    email = activities["Chess Club"]["participants"][0]
    # Act
    response = client.delete("/activities/Chess Club/unregister", params={"email": email})
    # Assert
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_not_signed_up():
    response = client.delete("/activities/Chess Club/unregister", params={"email": "x@y.z"})
    assert response.status_code == 400
