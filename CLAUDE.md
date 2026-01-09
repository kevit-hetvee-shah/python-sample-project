# CLAUDE.md - Project Conventions & Guidelines

> This file documents all project conventions, patterns, and configurations for consistent code generation.
> **Python Version**: 3.12+

---

## Project Overview

- **Framework**: FastAPI 0.128.0 with Uvicorn ASGI server
- **Language**: Python 3.12+
- **Database**: SQLite with SQLAlchemy 2.0 ORM
- **Authentication**: JWT (python-jose) with Bcrypt password hashing
- **Validation**: Pydantic 2.12.5

---

## Folder Structure

```
sample-project-backend/
├── apps/
│   └── fastapi/
│       ├── app.py                 # FastAPI application entry point
│       ├── __init__.py            # Package initialization with logger
│       └── src/
│           ├── auth.py            # Authentication utilities (JWT, password hashing)
│           ├── migrations.py      # Database migrations and seeding
│           ├── models.py          # SQLAlchemy ORM models
│           ├── response_models.py  # Standardized API response structures
│           ├── routes.py          # API route definitions
│           └── schemas.py         # Pydantic schemas for validation
├── app.db                         # SQLite database file (generated)
├── requirements.txt              # Python dependencies
├── .gitignore                     # Git ignore file
└── CLAUDE.md                      # This file - project conventions
```

---

## Naming Conventions

### Files
- **Format**: `snake_case.py` (lowercase with underscores)
- **Examples**: `response_models.py`, `user_service.py`, `auth_middleware.py`
- **Descriptive**: Name files by their purpose/domain

### Classes
- **Format**: `PascalCase` (capitalize each word)
- **SQLAlchemy Models**: Singular noun (e.g., `User`, `Product`, `Order`)
- **Pydantic Schemas**: Descriptive with suffix (e.g., `ProductCreate`, `UserResponse`, `LoginRequest`)

### Functions
- **Format**: `snake_case` (lowercase with underscores)
- **Use descriptive verbs**: `get_user_by_id`, `create_product`, `verify_password`
- **Handlers**: Prefix with HTTP method for route handlers (e.g., `get_products`, `create_user`)

### Variables
- **Local variables**: `snake_case` (e.g., `current_user`, `db_session`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Private**: Prefix with single underscore (e.g., `_internal_helper`)

---

## Database Conventions

### ORM: SQLAlchemy 2.0

#### Connection
```python
# Database: SQLite at ./app.db
# Connection string: sqlite:///./app.db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

engine = create_engine(
    "sqlite:///./app.db",
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
```

#### Session Management (Dependency Injection)
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### Model Definition Pattern
```python
from sqlalchemy import String, Integer, Float, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

class ModelName(Base):
    __tablename__ = "table_name"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    optional_field: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    # Add indexes for frequently queried fields
```

#### Field Types Mapping
| Python Type | SQLAlchemy Column | Max Length |
|-------------|-------------------|------------|
| `str` | `String(N)` | Specify N |
| `int` | `Integer` | - |
| `float` | `Float` | - |
| `bool` | `Boolean` | - |
| `Optional[str]` | `String(N), nullable=True` | Specify N |
| `str` (long text) | `Text` | Unlimited |

#### Common Patterns
- **Primary Key**: Always `id` as Integer with autoincrement
- **Timestamps**: Add `created_at`, `updated_at` if needed (use `DateTime`)
- **Soft Deletes**: Add `is_deleted` Boolean flag instead of deleting rows
- **Indexes**: Add `index=True` for frequently queried fields (e.g., `username`, `email`)

---

## API Response Structure

### Standard Response Format (from `response_models.py`)

```python
{
    "success": bool,        # True/False
    "status_code": int,     # HTTP status code
    "message": str,         # Descriptive message
    "data": any | None      # Response payload (optional)
}
```

### Success Responses
```python
# Single item
{
    "success": True,
    "status_code": 200,
    "message": "User retrieved successfully",
    "data": {"id": 1, "username": "john_doe"}
}

# List of items
{
    "success": True,
    "status_code": 200,
    "message": "Products retrieved successfully",
    "data": [{"id": 1, "name": "Product A"}, {"id": 2, "name": "Product B"}]
}

# Created
{
    "success": True,
    "status_code": 201,
    "message": "User created successfully",
    "data": {"id": 1, "username": "new_user"}
}
```

### Error Responses
```python
{
    "success": False,
    "status_code": 400,  # or 401, 404, 422, 500
    "message": "Error description",
    "data": None  # Optional: validation errors details
}
```

### Status Code Usage
| Code | Usage |
|------|-------|
| 200 | Successful GET, PUT, DELETE |
| 201 | Successful POST (resource created) |
| 400 | Bad request (invalid input) |
| 401 | Unauthorized (missing/invalid token) |
| 404 | Resource not found |
| 422 | Validation error (use Pydantic ValidationError) |
| 500 | Internal server error |

---

## Pydantic Schema Conventions

### Request Schemas (Input)
```python
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    email: Optional[EmailStr] = None
    city: Optional[str] = Field(None, max_length=100)

    @field_validator('password')
    @classmethod
    def passwords_match(cls, v: str) -> str:
        # Add custom validation logic
        return v
```

### Response Schemas (Output)
```python
class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    city: Optional[str] = None

    model_config = {"from_attributes": True}
```

### Update Schemas
```python
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    city: Optional[str] = Field(None, max_length=100)
    # All fields optional for partial updates
```

---

## Route/Endpoint Conventions

### Route Definition Pattern
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/resource", tags=["Resource"])

@router.get("/", response_model=StandardResponse)
def get_items(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # For protected routes
):
    """Get all items with pagination."""
    pass
```

### URL Patterns
- **Collections**: `/api/v1/resources` (plural)
- **Single item**: `/api/v1/resources/{id}`
- **Nested**: `/api/v1/users/{user_id}/posts`
- **Actions**: `/api/v1/resources/{id}/archive`

### Route Organization
```python
# routes.py structure
from fastapi import APIRouter

# Group routes by domain
auth_router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])
user_router = APIRouter(prefix="/api/v1/users", tags=["Users"])
product_router = APIRouter(prefix="/api/v1/products", tags=["Products"])

# Include routers in app.py
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(product_router)
```

---

## Authentication & Authorization

### JWT Configuration
```python
# JWT Settings
SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
```

### Protected Route Pattern
```python
from fastapi import Depends, HTTPException, status
from src.auth import get_current_user

@router.post("/protected")
def protected_endpoint(current_user: User = Depends(get_current_user)):
    """Requires valid JWT token."""
    return {"user": current_user.username}
```

### Optional Auth (Allow Anonymous)
```python
from fastapi import Depends
from typing import Optional

from src.auth import get_current_user, User

@router.get("/public")
def public_endpoint(current_user: Optional[User] = Depends(get_current_user)):
    """Accessible with or without auth token."""
    if current_user:
        return {"message": f"Hello {current_user.username}"}
    return {"message": "Hello anonymous"}
```

---

## Error Handling

### Centralized Exception Handlers (in `app.py`)
```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "status_code": 422,
            "message": "Validation error",
            "data": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "status_code": 500,
            "message": "Internal server error",
            "data": None
        }
    )
```

---

## Code Style (Python 3.12+)

### Type Hints (Required)
```python
# Always use type hints
from typing import Optional, List

def get_user(db: Session, user_id: int) -> Optional[User]:
    """Retrieve a user by ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Retrieve all users with pagination."""
    return db.query(User).offset(skip).limit(limit).all()
```

### Python 3.12+ Features
```python
# Use new union syntax (PEP 604)
# Instead of: Optional[int] or Union[int, None]
def process(value: int | None) -> str:
    return str(value)

# Use generic types without importing from typing
from collections.abc import Sequence

def get_items(ids: Sequence[int]) -> list[dict]:
    return [{"id": i} for i in ids]
```

### Docstrings
```python
def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user in the database.

    Args:
        db: Database session
        user: User creation data from request

    Returns:
        User: The created user instance
    """
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

---

## CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Database Query Patterns

### Common Queries
```python
# Get by ID
def get_by_id(db: Session, model_class, item_id: int):
    return db.query(model_class).filter(model_class.id == item_id).first()

# Get all with pagination
def get_all(db: Session, model_class, skip: int = 0, limit: int = 100):
    return db.query(model_class).offset(skip).limit(limit).all()

# Filter by field
def get_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Create
def create(db: Session, item_dict: dict):
    db_item = User(**item_dict)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# Update
def update(db: Session, item: User, updates: dict):
    for field, value in updates.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item

# Delete (soft delete preferred)
def soft_delete(db: Session, item: User):
    item.is_deleted = True
    db.commit()
    return item
```

---

## Environment Variables

Create a `.env` file (add to `.gitignore`):
```env
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./app.db
```

---

## API Documentation

FastAPI auto-generates docs at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Add endpoint descriptions:
```python
@router.post(
    "/register",
    response_model=StandardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with username and password"
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    pass
```

---

## Quick Templates

### New Model Template
```python
# src/models.py
class NewModel(Base):
    __tablename__ = "new_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
```

### New Schema Template
```python
# src/schemas.py
class NewModelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class NewModelResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}
```

### New Route Template
```python
# src/routes.py
@router.post("/", response_model=StandardResponse, status_code=201)
def create_new_model(
    item: NewModelCreate,
    db: Session = Depends(get_db)
):
    """Create a new item."""
    db_item = NewModel(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return StandardResponse(
        success=True,
        status_code=201,
        message="Item created successfully",
        data=NewModelResponse.model_validate(db_item).model_dump()
    )

@router.get("/", response_model=StandardResponse)
def get_items(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get all items with pagination."""
    items = db.query(NewModel).offset(skip).limit(limit).all()
    return StandardResponse(
        success=True,
        status_code=200,
        message="Items retrieved successfully",
        data=[NewModelResponse.model_validate(i).model_dump() for i in items]
    )
```

---

## Common Imports

```python
# Database
from sqlalchemy import String, Integer, Float, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, Session
from apps.fastapi.src.models import Base, User, Product  # Import models as needed

# FastAPI
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Pydantic
from pydantic import BaseModel, Field, EmailStr, field_validator

# Auth
from apps.fastapi.src.auth import get_current_user, get_password_hash, verify_password
from apps.fastapi.src.response_models import StandardResponse

# Types
from typing import Optional, List
```

---

## Testing Data Seeding

For development, add dummy data in `migrations.py`:
```python
def seed_dummy_data(db: Session):
    """Seed database with test data."""
    # Add dummy users with hashed passwords
    dummy_users = [
        User(username="user1", password=get_password_hash("password123")),
        User(username="user2", password=get_password_hash("password123")),
    ]
    db.add_all(dummy_users)
    db.commit()
```
