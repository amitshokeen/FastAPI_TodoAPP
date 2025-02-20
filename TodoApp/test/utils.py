from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..main import app, appX
from fastapi.testclient import TestClient
import pytest
from ..models import Todos, Users
from ..routers.auth import bcrypt_context

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
		SQLALCHEMY_DATABASE_URL,
		connect_args={"check_same_thread": False},
        poolclass=StaticPool
	)

TestingSessionLocal = sessionmaker(
	    autocommit=False, 
		autoflush=False, 
		bind=engine
    )

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username': 'd203', 'id': 1, 'user_role': 'admin'}

def override_get_current_user_non_admin():
    return {'username': 'd203', 'id': 1, 'user_role': 'non_admin'}

client = TestClient(app) # we wrap our app with a TestClient
clientX = TestClient(appX)

@pytest.fixture
def test_todo():
    db = TestingSessionLocal()
    
    todo = Todos(
        title="Learn to code!",
        description="Need to learn everyday!",
        priority=5,
        complete=False,
        owner_id=1
    )
    db.add(todo)
    db.commit()
    yield todo

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

@pytest.fixture
def test_user():
    user = Users(
        username= 'testD203',
        email= 'testD203@email.com',
        first_name="TestAmit",
        last_name="TestShokeen",
        hashed_password=bcrypt_context.hash("passw0rdI2E"),
        role="admin",
        phone_number="0102020202"
    )
    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()


