from .database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String) # we store the hashed password in the db. That way, the app developer is unable to know the user's password. So, while logging in, when a user enters his password in plain-text, the password is re-hashed and then it is compared to the hashed password already present in the DB. Even if the db is hacked, the passwords are secure because they are hashed. 
    is_active = Column(Boolean, default=True)
    role = Column(String) # to cater for roles like 'admin' etc.
    phone_number = Column(String)

class Todos(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))