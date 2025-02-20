from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Todos
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)
def get_db():
    db = SessionLocal() # Create a new database session
    try:
        yield db # Provide the session to the request handler
    finally:
        db.close() # Close the session after request is completed

# This line ensures that the get_db() is called whenever a route requires a database session.
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get('/todo', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed!')
    return db.query(Todos).all()

@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
        user: user_dependency,
        db: db_dependency,
        todo_id: int = Path(ge=1)
    ):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed!')
    
    todo_model = db.query(Todos)\
        .filter(Todos.id == todo_id)\
        .first()
    
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found!")
    
    db.query(Todos)\
        .filter(Todos.id == todo_id)\
        .delete()

    db.commit()
