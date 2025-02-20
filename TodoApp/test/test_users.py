from ..main import app
from ..routers.users import get_db, get_current_user
from fastapi import status
from ..models import Users
from .utils import *

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'testD203'
    assert response.json()['email'] == 'testD203@email.com'
    assert response.json()['first_name'] == 'TestAmit'
    assert response.json()['last_name'] == 'TestShokeen'
    assert response.json()['role'] == 'admin'
    assert response.json()['phone_number'] == '0102020202'
    assert response.json()['is_active'] == True
    assert response.json()['id'] == 1
    
def test_change_password_success(test_user):
    response = client.put(
        "/user/password", 
        json={
            "password": "passw0rdI2E", 
            "new_password": "newPassword123"
        }
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_invalid_current_password(test_user):
    response = client.put(
        "/user/password", 
        json={
            "password": "wrong_password", 
            "new_password": "newPassword123"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail':'Error on password change'}

def test_change_phone_number_success(test_user):
    response = client.put("/user/phonenumber/0435")
    assert response.status_code == status.HTTP_204_NO_CONTENT
