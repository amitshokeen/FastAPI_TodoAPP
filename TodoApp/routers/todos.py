"""
1. This todos.py is going to need two lines that our auth.py has, i.e. `from fastapi import APIRouter
router = APIRouter()`

2. Now, copy everything from the main.py file and paste it inside the todos.py file. Even overwrite the stuff written by instructions in point 1 above.

3. Make this line: `app = FastAPI()` to `router = APIRouter()`
Also, change this line: `from fastapi import FastAPI` to `from fastapi import APIRouter`

4. Remove the line: `app.include_router(auth.router)` from the todos.py file.

5. Remove the line: `models.Base.metadata.create_all(bind=engine)` from the todos.py file.

6. Remove the `engine` import.

7. Remove `from routers import auth`

8. Remove `import models`

9. Now, go to all your API endpoints and replace `app` with `router`

10. Now, go to your main.py file and also import `todos` like so: `from routers import auth, todos`

11. In the main.py file, add this line as well: `app.include_router(todos.router)`. Let this line be after this line: `app.include_router(auth.router)`

12. Delete everything else from the main.py file. >> or better do this -> copy the main.py to main_old.py (so that I can refer to it later to revise), then delete all code after this line `app.include_router(todos.router)`

13. Now, delete all of the un-needed imports that we have in our heavily modified main.py file.

14. All this is done to clean up our application for scalability and maintainability. It brings us a step closer to implementing authentication and authorization within our application.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Todos
"""
# This is our auth.py function that allows us to validate the JWT, get the payload and turn it into a username and user_id.
"""
from .auth import get_current_user
from fastapi.templating import Jinja2Templates
#from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

templates = Jinja2Templates(directory="TodoApp/templates")

router = APIRouter(
    prefix='/todos',
    tags=['todos']
)

"""
* Here 'models.Base' is the base class for all database tables
* 'metadata.create_all(bind=engine)' -> This tells SQLAlchemy to look at all the models in models.py and create the tables if they don't already exist.
* A point to note here is that, if we enhance the tables in 'models.py', then this line below will not be automatically ran.
* So, it's easier to delete the 'todos.db' and then re-create it.
* 'Alembic' can help in this regard as it will let us enhance the DB without deleting each time.
"""

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
user_dependency = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    # Note that 'id' is not passed in into the request.  For obvious reasons, we don't want to be inputting this in the request. Luckily, SQLAlchemy will take care of this because the 'id' has been described in the model as the primary key.
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(ge=1, le=5)
    complete: bool

def redirect_to_login():
    redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response

### Pages ###

# here we do 'template rendering'
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token')) # this will get our JWT
        
        if user is None:
            return redirect_to_login()

        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()

        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})
    
    except:
        return redirect_to_login()


@router.get("/add-todo-page")
async def render_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token')) # this will get our JWT

        if user is None:
            return redirect_to_login()
        
        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})
    
    except:
        return redirect_to_login()
    
@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token')) # this will get our JWT

        if user is None:
            return redirect_to_login()
        
        todo = db.query(Todos).filter(Todos.id == todo_id).first()

        return templates.TemplateResponse("edit-todo.html", {"request": request, "user": user, "todo": todo})
        
    except:
        return redirect_to_login()

### Endpoints ###
"""
This GET request injects a database session using db_dependency.
It queries all rows from the Todos table.
The result is returned as JSON.
"""
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(
        user: user_dependency,
        db: db_dependency,
    ):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(
        user: user_dependency,
        db: db_dependency, 
        todo_id: int = Path(ge=1)
    ):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = db.query(Todos)\
        .filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id'))\
        .first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found')

@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(
        user: user_dependency, 
        db: db_dependency, 
        todo_request: TodoRequest
    ):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    """
    Q. Why do we need this `owner_id=user.get('id')` in the line of code below?
    A. Notice the `class Todos` in models.py. It has a column named `owner_id`.
    Now notice that `todo_request: TodoRequest` lacks this `owner_id`...for obvious reasons.
    So, we have to supply the owner_id explicitly in the line of code below.
     - & we get this owner_id from `user_dependency` ... trace back to it and notice that it depends on `get_current_user` from the auth.py file. Notice that `get_current_user` returns a dictionary containing the owner_id as well.
     It all ties up well together because the `owner_id` is the foreign-key in the Todos table and is the primary-key in the Users table.
    """
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))
    db.add(todo_model) # here we are making the DB ready
    db.commit() # here we are flushing it all and actually doing the transaction to the DB
"""
After the above `create_todo` is modified with the addition of `user_dependency`, you will notice that the corresponding swagger path will show a lock like icon - indicating that you got to login to get this working.
"""


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
        user: user_dependency,
        db: db_dependency, 
        todo_request: TodoRequest, # this is a non-default argument
        todo_id: int = Path(ge=1) # this is a default argument because it deals with a path parameter and so must be the last argument. This is a python rule.
    ):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    todo_model = db.query(Todos)\
        .filter(Todos.owner_id == user.get('id'))\
        .filter(Todos.id == todo_id)\
        .first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    """
    Careful! Don't use the line below that uses the model_dump(). 
    Why? Because it uses the Todos model in full - the SQLAlchemy will do it's magic, needlessly, and increment the value of primary key, i.e. id, of the Todos table. That will create an effect of a POST - a new Todo will get added. So, do as in the 4 lines above, i.e., explicitly assign the values of title, description, priority, and complete as extracted from the request body.
    """
    #todo_model = Todos(**todo_request.model_dump())

    db.add(todo_model)
    db.commit()
    
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
        user: user_dependency,
        db: db_dependency, 
        todo_id: int = Path(ge=1)
    ):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    
    todo_model = db.query(Todos)\
        .filter(Todos.owner_id == user.get('id'))\
        .filter(Todos.id == todo_id)\
        .first()
    
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")
    
    db.query(Todos)\
        .filter(Todos.owner_id == user.get('id'))\
        .filter(Todos.id == todo_id)\
        .delete()

    db.commit()