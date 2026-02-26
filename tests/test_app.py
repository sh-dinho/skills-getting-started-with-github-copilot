import copy
import pytest

from fastapi.testclient import TestClient

from src import app

# create a client for the FastAPI application
client = TestClient(app.app)

# capture the initial activities dictionary so tests can reset to it
INITIAL_ACTIVITIES = copy.deepcopy(app.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset app.activities before each test (AAA pattern: Arrange part of each test)."""
    app.activities = copy.deepcopy(INITIAL_ACTIVITIES)
    yield


def test_get_activities():
    # Arrange is done by the fixture

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    # Arrange
    email = "test@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert email in app.activities["Chess Club"]["participants"]
    assert response.json()["message"] == f"Signed up {email} for Chess Club"


def test_signup_duplicate():
    # Arrange
    existing = INITIAL_ACTIVITIES["Chess Club"]["participants"][0]

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup", params={"email": existing}
    )

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_activity_not_found():
    # Act
    response = client.post(
        "/activities/NoSuch/signup", params={"email": "a@b.com"}
    )

    # Assert
    assert response.status_code == 404


def test_unregister_success():
    # Arrange
    to_remove = INITIAL_ACTIVITIES["Chess Club"]["participants"][0]

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants", params={"email": to_remove}
    )

    # Assert
    assert response.status_code == 200
    assert to_remove not in app.activities["Chess Club"]["participants"]
    assert "Unregistered" in response.json()["message"]


def test_unregister_not_found():
    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants", params={"email": "noone@mergington.edu"}
    )

    # Assert
    assert response.status_code == 404


def test_unregister_activity_not_found():
    # Act
    response = client.delete(
        "/activities/DoesntExist/participants", params={"email": "a@b.com"}
    )

    # Assert
    assert response.status_code == 404
