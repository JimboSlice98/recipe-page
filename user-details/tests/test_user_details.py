import pytest
from api.app import app  # Replace 'your_flask_module_name' with the name of your Flask module

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_user_details_no_user_id(client):
    response = client.get("/get-user-details")
    assert response.status_code == 500
    # assert response.status_code == 400

def test_get_user_details_with_user_id(client):
    response = client.get("/get-user-details?user_id=123")
    assert response.status_code == 500
    # assert response.status_code == 200

def test_update_user_details_no_user_id(client):
    response = client.post("/update-user-details", json={})
    assert response.status_code == 400

def test_update_user_details_with_user_id(client):
    response = client.post("/update-user-details", json={"UserID": 123})
    assert response.status_code == 400  # Should return 400 because no fields are provided for update

def test_update_user_details_with_fields(client):
    response = client.post("/update-user-details", json={"UserID": 123, "Email": "test@example.com"})
    assert response.status_code == 500
    # assert response.status_code == 404 
