from .utils import *
from ..routers.admin import get_db, get_current_user
from ..main import app, appX
from ..models import Todos
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
appX.dependency_overrides[get_current_user] = override_get_current_user_non_admin

"""
Note: the test below will only pass if the function named 'override_get_current_user' in the 'utils.py' file returns 'user_role' as 'admin'. So make sure 'user_role' is set as 'admin'.
"""
def test_admin_read_all_authenticated(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
            'title': 'Learn to code!', 
            'description': 'Need to learn everyday!', 
            'complete': False, 
            'priority': 5, 
            'id': 1, 
            'owner_id': 1
        }]

def test_admin_read_all_authenticated_non_admin(test_todo):
    response = clientX.get("/admin/todo")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Authentication Failed!'}

def test_admin_delete_todo(test_todo):
    response = client.delete("/admin/todo/1")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_admin_delete_todo_not_found():
    response = client.delete("/admin/todo/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found!'}