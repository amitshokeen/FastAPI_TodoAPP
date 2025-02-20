from fastapi import Body, FastAPI

app = FastAPI()

BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]

@app.get("/")
async def first_api():
    return {"message": "Hello Amit!"}

@app.get("/books")
async def read_all_books():
    return BOOKS

@app.get("/books/mybook")
async def read_all_books():
    return {'dynamic_param': 'Stumbling into infinity'}

@app.get("/books/{book_title}")
async def read_all_books(book_title: str):
    for book in BOOKS:
        # casefold() is a stronger form of lowercase(). It will even convert characters from other languages to lowercase.
        if book.get('title').casefold() == book_title.casefold():
            return book
    return None

@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book['category'].casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return

@app.get("/books/authorbyquery/")
async def get_all_books_for_author_by_query(author: str):
    book_list = []
    for book in BOOKS:
        if book.get("author").casefold() == author.casefold():
            book_list.append(book)
    return book_list


@app.get("/books/{book_author}/")
async def read_author_category_by_query(book_author: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if (book.get('author').casefold() == book_author.casefold()) and \
            (book.get('category') == category.casefold()):
            books_to_return.append(book)
    return books_to_return

@app.post("/book/create_book")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)

@app.put("/books/update_book")
async def update_book(update_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == update_book.get('title').casefold():
            BOOKS[i] = update_book

@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book_title.casefold():
            BOOKS.pop(i)
            break

@app.get("/books/author/{author}")
async def get_all_books_for_author(author: str):
    book_list = []
    for book in BOOKS:
        if book.get("author").casefold() == author.casefold():
            book_list.append(book)
    return book_list



