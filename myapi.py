# from fastapi import FastAPI, Path
# from typing import Optional
# from pydantic import BaseModel



# app = FastAPI()

# students = {
#     1: {
#         "name" : "john",
#         "age" : 12,
#         "year" : "year 12"
#     }
# }

# class Student(BaseModel):
#     name: str
#     age: int
#     year: str


# class UpdateStudent(BaseModel):
#     name: Optional[str] = None
#     age: Optional[int] = None
#     year: Optional[str] = None


# @app.get("/")
# def index():
#     return {"name" : "First Data"}


# @app.get("/get-student/{student_id}")
# def get_student(student_id: int = Path(description="The ID of the student you want to view: ", gt = 0, lt = 3)):
#     return students[student_id]


# @app.get("/get-by-name")
# def get_student(*, name: Optional[str] = None, test: int):
#     for student_id in students:
#         if students[student_id]["name"] == name:
#             return students[student_id]
    
#     return {"Data" : "Not found"}


# @app.post("/create-student/{student_id}")
# def create_student(student_id :  int, student : Student):
#     if student_id in students:
#         return {"Error": "Student exists"}
    
#     students[student_id] = student
#     return students[student_id]


# @app.put("/update-student/{student_id}")
# def update_student(student_id: int, student: UpdateStudent):
#     if student_id not in students:
#         return {"Error": "Student does not exist"}
    
#     if student.name != None:
#         students[student_id].name = student.name
    
#     if student.age != None:
#         students[student_id].age = student.age
    
#     if student.year != None:
#         students[student_id].year = student.year

#     return students[student_id]


# @app.delete("/delete-student/{student_id}")
# def delete_student(student_id: int):
#     if student_id not in students:
#         return {"Error": "No such student exist"}
    
#     del students[student_id]
#     return {"Error": "Students deleted successfully."}

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import mysql.connector

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Connect to the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="library_db"
)

# Create a cursor object to execute MySQL queries
cursor = db.cursor()

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("add.html", {"request": request})


@app.post("/add-book")
async def add_book(request: Request):
    form_data = await request.form()
    book_id = form_data["book_id"]
    title = form_data["title"]
    author_name = form_data["author_name"]
    number_of_books = form_data["number_of_books"]
    
    # Insert the book into the database
    query = "INSERT INTO books (id, title, author_name, number_of_books) VALUES (%s, %s, %s, %s)"
    values = (book_id, title, author_name, number_of_books)
    cursor.execute(query, values)
    db.commit()
    
    context = {"request": request, "message": "Book added successfully"}
    return templates.TemplateResponse("add.html", context)



@app.route("/update-book", methods=["PUT", "POST"])
async def update_book(request: Request):
    if request.method == "PUT" or request.method == "POST":
        form_data = await request.form()
        book_id = form_data["book_id"]
        title = form_data["title"]
        author = form_data["author"]
        number_of_books = form_data["number_of_books"]

        # Update the book details in the database
        query = "UPDATE books SET title = %s, author_name = %s, number_of_books = %s WHERE id = %s"
        values = (title, author, number_of_books, book_id)
        cursor.execute(query, values)
        db.commit()

        context = {"request": request, "message": "Book updated successfully"}
        return templates.TemplateResponse("add.html", context)

    raise HTTPException(status_code=405, detail="Method Not Allowed")
    


@app.get("/delete-book")
async def delete_book(request: Request):
    book_id = request.query_params["book_id"]
    
    # Delete the book from the database
    query = "DELETE FROM books WHERE id = %s"
    cursor.execute(query, (book_id,))
    db.commit()
    
    context = {"request": request, "message": "Book deleted successfully"}
    return templates.TemplateResponse("add.html",context)


@app.get("/dashboard")
async def dashboard(request: Request):
    # Fetch books data from the database
    query = "SELECT * FROM books"
    cursor.execute(query)
    books_data = cursor.fetchall()

    # Convert the fetched data into a list of dictionaries
    books = []
    for book in books_data:
        book_dict = {
            "id": book[0],
            "title": book[1],
            "author_name": book[2],
            "number_of_books": book[3]
        }
        books.append(book_dict)


    # Pass the books data to the template
    context = {"request": request, "books": books}
    return templates.TemplateResponse("dashboard.html", context)



