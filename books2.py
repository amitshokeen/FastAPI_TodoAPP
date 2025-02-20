from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field, field_validator
from starlette import status

app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    published_date: int
    rating: int

    def __init__(self, id, title, author, description, published_date, rating):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.published_date = published_date
        self.rating = rating

class BookRequest(BaseModel):
    id: Optional[int] = Field(description='ID is not needed on create', default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    published_date: int
    rating: int = Field(gt=0, lt=6)

    @field_validator('published_date')
    def validate_published_date(cls, value):
        current_year = datetime.now().year
        if not (1450 <= value <= current_year):
            raise ValueError(f'published_date must be between 1450 and {current_year}')
        return value
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A new description of a book",
                "published_date": 2012,
                "rating": 5
            }
        }
    }

BOOKS = [
    Book(1, 'Computer Science Pro', 'codingwithroby', 'A very nice book!', 2024, 5),
    Book(2, 'Be Fast with FastAPI', 'codingwithroby', 'A great book!', 2025, 5),
    Book(3, 'Master Endpoints', 'codingwithroby', 'An awesome book!', 2000, 5),
    Book(4, 'HP1', 'Author 1', 'Book Description', 1989, 2),
    Book(5, 'HP2', 'Author 2', 'Book Description', 1801, 3),
    Book(6, 'HP3', 'Author 3', 'Book Description', 1945, 1)
]

@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail='Item not found')

@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_by_rating(book_rating: int = Query(ge=1, le=5)):
    books_by_rating = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_by_rating.append(book)
    return books_by_rating

@app.post("/create-book", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
    """
    * The below line is performing data conversion from a Pydantic model (BookRequest) to a Python class (Book).
    * book_request is a pydantic model instance (BookRequest). It contains the data sent in the request body. Pydantic ensures validation (e.g., min/max values for fields).
    * book_request.model_dump() converts the Pydantic model to a Python dictionary.
    >> so book_request.model_dump() returns this dictionary: 
    `{
        "title": "A new book",
        "author": "codingwithroby",
        "description": "A new description of a book",
        "published_date": 2012,
        "rating": 5
    }`
    * Then `**book_request.model_dump()` unpacks the dictionary and passes it as keyword args (kwargs) to the Book constructor like this:
    `new_book = Book(
        title="A new book",
        author="codingwithroby",
        description="A new description of a book",
        published_date=2012,
        rating=5
    )`
    * This creates a Book instance using the validated data.
    """
    new_book = Book(**book_request.model_dump())  
    print(f"****>> {type(new_book)}")
    BOOKS.append(find_book_id(new_book))

def find_book_id(book: Book):
    book.id = BOOKS[-1].id + 1 if len(BOOKS) > 0 else 1
    return book

@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book_to_update: BookRequest):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_to_update.id:
            BOOKS[i] = book_to_update
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')
    """
        # The below approach will not work because this loop iterates
        # over each book in BOOKS, but the assignment `book = updated_book`
        # only changes the local variable `book` within the loop. 
        # It does not affect the original list BOOKS.

        # for book in BOOKS:
        #     if book.id == book_to_update.id:
        #         book = book_to_update
        
        # But, this approach can be modified to achieve the intended task of 
        # modifying the original list. Do this:

        # for i, book in enumerate(BOOKS):
        #     if book.id == book_to_update.id:
        #         BOOKS[i] = book_to_update

        # This modification uses the `enumerate()` function to iterate over 
        # both the index and the book object in the BOOKS list.
        # By using the index `i`, we can directly update the element in the 
        # original list when a match is found.
        # This code is more Pythonic.
    """


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book_by_id(book_id: int = Path(ge=1, le=len(BOOKS))):
    book_changed = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)  # `del BOOKS[i]` can also be used
            book_changed = True
            break
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')
    
@app.get("/books/published-date/", status_code=status.HTTP_200_OK)
async def read_book_by_published_date(published_date: int = Query(ge=1450, le=datetime.now().year)):
    # current_year = datetime.now().year
    # if not (1450 <= published_date <= current_year):
    #     return {"error": f"published_date must be between 1450 and {current_year}"}
    
    list_of_books = []
    for book in BOOKS:
        if book.published_date == published_date:
            list_of_books.append(book)
    
    return list_of_books