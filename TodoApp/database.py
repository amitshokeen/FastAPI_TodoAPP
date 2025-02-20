from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Means we are using an SQLite database file called todos.db (stored in the current directory ./)
# you can delete the todos.db now.
#SQLALCHEMY_DATABASE_URL = 'sqlite:///./todos.db' 
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'

# Connects FastAPI to the database
engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={'check_same_thread': False}
    )

# Manages database sessions - here you write data before saving
SessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=engine
    )

# Lets us define tables easily
Base = declarative_base()