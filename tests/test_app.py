import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Helper to reset activities state before each test
def reset_activities():
    for activity in activities.values():
        activity["participants"] = []

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    # Arrange: Reset activities before each test
    reset_activities()
    yield
    reset_activities()

def test_list_activities():
    # Arrange
    # (Nothing to set up, state is clean)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_success():
    # Arrange
    email = "test1@mergington.edu"
    # Act
    response = client.post("/activities/Chess Club/signup?email=" + email)
    # Assert
    assert response.status_code == 200
    assert email in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    # Arrange
    email = "test2@mergington.edu"
    activities["Chess Club"]["participants"].append(email)
    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"

def test_signup_full():
    # Arrange
    email = "test3@mergington.edu"
    activities["Chess Club"]["participants"] = [f"user{i}@m.edu" for i in range(activities["Chess Club"]["max_participants"])]
    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"

def test_unregister_success():
    # Arrange
    email = "test4@mergington.edu"
    activities["Chess Club"]["participants"].append(email)
    # Act
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")
    # Assert
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]

def test_unregister_not_found():
    # Arrange
    email = "notfound@mergington.edu"
    # Act
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
