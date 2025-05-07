from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
# from datetime import timedelta
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from typing import List

# FastAPI app
app = FastAPI()

# OAuth2 for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Config values
SECRET_KEY = "ABCD321"  # Use env var in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fake user database
fake_users_db = {
    "chinna": {
        "username": "chinna",
        "full_name": "Chinna Dev",
        "hashed_password": pwd_context.hash("password123"),
    }
}

# Fake book database (in-memory storage)
fake_books_db = []

# Book Pydantic model for request validation
class Book(BaseModel):
    id: int
    title: str
    author: str
    description: str
    price: float

# Function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Function to authenticate user
def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user

# Function to create access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Token generation route
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected route to get user info
@app.get("/protected")
def read_protected(current_user: str = Depends(oauth2_scheme)):
    return {"message": f"Hello, {current_user}. You have access!"}

# Route to add a book
@app.post("/books")
def add_book(book: Book, current_user: str = Depends(oauth2_scheme)):
    # Check if book with the same id already exists
    if any(b.id == book.id for b in fake_books_db):
        raise HTTPException(status_code=400, detail="Book with this ID already exists")
    fake_books_db.append(book)
    return book

# Route to retrieve all books
@app.get("/books", response_model=List[Book])
def get_books(current_user: str = Depends(oauth2_scheme)):
    return fake_books_db

# Route to retrieve a single book by id
@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, current_user: str = Depends(oauth2_scheme)):
    for book in fake_books_db:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")
