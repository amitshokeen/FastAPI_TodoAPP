"""
'main.py' starts the FastAPI app. 
It creates the DB tables using SQLAlchemy.
It connects FastAPI to the DB using 'engine'.
It runs the API when executed with Uvicorn.
"""

from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal
from models import Todos
from routers import auth, todos # all the authentication stuff is here

app = FastAPI()

"""
* Here 'models.Base' is the base class for all database tables
* 'metadata.create_all(bind=engine)' -> This tells SQLAlchemy to look at all the models in models.py and create the tables if they don't already exist.
* A point to note here is that, if we enhance the tables in 'models.py', then this line below will not be automatically ran.
* So, it's easier to delete the 'todos.db' and then re-create it.
* 'Alembic' can help in this regard as it will let us enhance the DB without deleting each time.
"""
models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router) # with this line, it becomes possible for the main.py to use the auth.py for authentication
app.include_router(todos.router)


"""
Instead of manually creating and closing sessions in every route, the below function makes sure that sessions are properly managed.
"""
def get_db():
    db = SessionLocal() # Create a new database session
    try:
        yield db # Provide the session to the request handler
    finally:
        db.close() # Close the session after request is completed

# This line ensures that the get_db() is called whenever a route requires a database sesion.
db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    # Note that 'id' is not passed in into the request.  For obvious reasons, we don't want to be inputting this in the request. Luckily, SQLAlchemy will take care of this because the 'id' has been described in the model as the primary key.
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(ge=1, le=5)
    complete: bool


"""
This GET request injects a database session using db_dependency.
It queries all rows from the Todos table.
The result is returned as JSON.
"""
@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()

@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(ge=1)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found')

@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.model_dump())

    db.add(todo_model) # here we are making the DB ready
    db.commit() # here we are flushing it all and actually doing the transaction to the DB

@app.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
                      db: db_dependency, 
                      todo_request: TodoRequest, # this is a non-default argument
                      todo_id: int = Path(ge=1) # this is a default argument because it deals with a path parameter and so must be the last argument. This is a python rule.
                     ):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()
    
@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
                        db: db_dependency, 
                        todo_id: int = Path(ge=1)
                    ):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")
    
    db.query(Todos).filter(Todos.id == todo_id).delete()

    db.commit()