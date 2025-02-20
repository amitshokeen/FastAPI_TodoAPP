from datetime import timedelta
from .utils import *
from ..routers.auth import get_db, get_current_user, authenticate_user, create_access_token, SECRET_KEY, ALGORITHM
from jose import jwt
import pytest
from fastapi import HTTPException, status

app.dependency_overrides[get_db] = override_get_db

def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username, "passw0rdI2E", db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_existent_user = authenticate_user('wrongUsername', 'somePwd', db)
    assert non_existent_user is False

    wrong_password_user = authenticate_user(test_user.username, 'wrongPassword', db)
    assert wrong_password_user is False

def test_create_access_token(test_user):
    username = test_user.username
    id = test_user.id
    role = test_user.role
    expires_delta = timedelta(minutes=20)

    token = create_access_token(username, id, role, expires_delta)

    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded_token.get('sub') == username
    assert decoded_token.get('id') == id
    assert decoded_token.get('role') == role

"""
Since we are testing an async function, so we need this test function to be async as well.
Btw, this test will only run if you have 'pytest-asyncio' already installed. If not installed, then do `pip install pytest-asyncio`. In addition, please don't forget to use the `@pytest.mark.asyncio` decorator.
"""
@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {'sub': 'testuser', 'id': 1, 'role': 'admin'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    user = await get_current_user(token=token)
    assert user == {'username':'testuser', 'id': 1, 'user_role': 'admin'}

"""
The below test verifies the behavior of the 'get_current_user' function when the JWT token is missing the required details.
First, the JWT token is created with incomplete info.
Then, `get_current_user(token=token)` is called - which is expected to raise an HTTPException.
The function checks that 401 Unauthorized error is raised.

Understanding `with pytest.raises(HTTPException) as excinfo:`
> This is the confusing part of the test. So let's clarify it.
> `with` is used for 'context management'
> It automatically handles setup and teardown for certain actions.
> A common use case is file handling: 

`with open("file.txt", "r") as file:
    content = file.read() # There is no need to manually close the file!`

> By using this line `pytest.raises(<expected exception>)`, you are saying this to 'pytest':
1. "I expect this code block to raise this specific exception"
2. If the exception is not raised, the test fails.
3. If the exeption is raised, it gets captured in 'excinfo'.
"""
@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {'role': 'user'}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)
    
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == 'Could not validate user.'
    
    