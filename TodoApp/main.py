"""
'main.py' starts the FastAPI app. 
It creates the DB tables using SQLAlchemy.
It connects FastAPI to the DB using 'engine'.
It runs the API when executed with Uvicorn.
"""

from fastapi import FastAPI, Request, status
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users
#from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()
appX = FastAPI()

"""
* Here 'models.Base' is the base class for all database tables
* 'metadata.create_all(bind=engine)' -> This tells SQLAlchemy to look at all the models in models.py and create the tables if they don't already exist.
* A point to note here is that, if we enhance the tables in 'models.py', then this line below will not be automatically ran.
* So, it's easier to delete the 'todos.db' and then re-create it.
* 'Alembic' can help in this regard as it will let us enhance the DB without deleting each time.
"""
#models.Base.metadata.create_all(bind=engine)
Base.metadata.create_all(bind=engine)

#templates = Jinja2Templates(directory="TodoApp/templates")

app.mount("/static", StaticFiles(directory="TodoApp/static"), name="static")

@app.get("/")
def test(request: Request):
    #return templates.TemplateResponse("home.html", {"request": request})
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)


@app.get("/healthy")
def health_check():
    return {"status": "healthy"}

app.include_router(auth.router) # with this line, it becomes possible for the main.py to use the auth.py for authentication
app.include_router(todos.router)
app.include_router(admin.router)
"""
The line below is not the usual way of doing stuff. I did this to be able to run this test 'test_admin_read_all_authenticated_non_admin'
"""
appX.include_router(admin.router) 
app.include_router(users.router)