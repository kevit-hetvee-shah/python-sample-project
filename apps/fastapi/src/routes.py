from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from src.models import get_db, Product, User
from src.schemas import (
    ProductCreate, ProductResponse, UserRegister, UserLogin,
    UserResponse, UserUpdate, TokenResponse
)
from src.auth import (
    get_current_user, authenticate_user, create_access_token,
    get_password_hash
)
from src.response_models import ApiResponse, ApiListResponse, ErrorResponse

router = APIRouter()

# ==================== USER ROUTES ====================

@router.get("/users", tags=["Users"])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    List all users with id, username, city, state, and landmark.
    Supports pagination with skip and limit parameters.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    response.status_code = status.HTTP_200_OK
    return ApiListResponse(
        success=True,
        status_code=200,
        message="Users retrieved successfully",
        data=[UserResponse.model_validate(u) for u in users]
    )


@router.get("/users/{user_id}", tags=["Users"])
def get_user(user_id: int, db: Session = Depends(get_db), response: Response = None):
    """
    Get a specific user by ID. Returns all user fields including id,
    username, city, state, and landmark.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(
            success=False,
            status_code=404,
            message=f"User with id {user_id} not found",
            details={"user_id": user_id}
        )
    response.status_code = status.HTTP_200_OK
    return ApiResponse(
        success=True,
        status_code=200,
        message="User retrieved successfully",
        data=UserResponse.model_validate(user)
    )


# ==================== PRODUCT ROUTES ====================

@router.get("/home", tags=["Home"])
def home(db: Session = Depends(get_db), response: Response = None):
    return ApiResponse(
        success=True,
        status_code=200,
        message="Home fetched successfully",
        data={"data": "Hello World!"}
    )

@router.get("/products", tags=["Products"])
def list_products(db: Session = Depends(get_db), response: Response = None):
    """
    List all products with id, name, price, description, and image_url.
    Returns 10 dummy products after running migrations.
    """
    products = db.query(Product).all()
    response.status_code = status.HTTP_200_OK
    return ApiListResponse(
        success=True,
        status_code=200,
        message="Products retrieved successfully",
        data=[ProductResponse.model_validate(p) for p in products]
    )


@router.post("/products", tags=["Products"])
def add_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    response: Response = None
):
    """
    Add a new product. Requires JWT authentication.
    ID will be auto-incremented.
    """
    new_product = Product(
        name=product.name,
        price=product.price,
        description=product.description,
        image_url=product.image_url
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    response.status_code = status.HTTP_201_CREATED
    return ApiResponse(
        success=True,
        status_code=201,
        message="Product added successfully",
        data=ProductResponse.model_validate(new_product)
    )


@router.get("/products/{product_id}", tags=["Products"])
def get_product(product_id: int, db: Session = Depends(get_db), response: Response = None):
    """
    Get a specific product by ID. Returns all fields including id, name,
    price, description, and image_url.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(
            success=False,
            status_code=404,
            message=f"Product with id {product_id} not found",
            details={"product_id": product_id}
        )
    response.status_code = status.HTTP_200_OK
    return ApiResponse(
        success=True,
        status_code=200,
        message="Product retrieved successfully",
        data=ProductResponse.model_validate(product)
    )


# ==================== AUTH ROUTES ====================

@router.post("/auth/register", tags=["Authentication"])
def register_user(user_data: UserRegister, db: Session = Depends(get_db), response: Response = None):
    """
    Register a new user with username, password, confirm password, and
    optional city, state, and landmark fields.
    Returns user details without token. Login to get token.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(
            success=False,
            status_code=400,
            message="Username already exists",
            details={"username": user_data.username}
        )

    # Create new user
    new_user = User(
        username=user_data.username,
        password=get_password_hash(user_data.password),
        city=user_data.city,
        state=user_data.state,
        landmark=user_data.landmark
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    response.status_code = status.HTTP_201_CREATED
    return ApiResponse(
        success=True,
        status_code=201,
        message="User registered successfully",
        data=UserResponse.model_validate(new_user)
    )


@router.post("/auth/login", tags=["Authentication"])
def login_user(user_credentials: UserLogin, db: Session = Depends(get_db), response: Response = None):
    """
    Login with username and password. Returns JWT access token.
    """
    user = authenticate_user(db, user_credentials.username, user_credentials.password)

    if not user:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return ErrorResponse(
            success=False,
            status_code=401,
            message="Incorrect username or password",
            details="Invalid credentials"
        )

    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )

    response.status_code = status.HTTP_200_OK
    return ApiResponse(
        success=True,
        status_code=200,
        message="Login successful",
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user)
        }
    )


# ==================== PROFILE ROUTES ====================

@router.get("/auth/profile", tags=["Profile"])
def view_profile(current_user: User = Depends(get_current_user), response: Response = None):
    """
    View the current user's profile. Requires JWT authentication.
    """
    response.status_code = status.HTTP_200_OK
    return ApiResponse(
        success=True,
        status_code=200,
        message="Profile retrieved successfully",
        data=UserResponse.model_validate(current_user)
    )


@router.put("/auth/profile", tags=["Profile"])
def update_profile(
    profile_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    Update the current user's profile (city, state, landmark).
    Requires JWT authentication.
    """
    # Update only provided fields
    if profile_update.city is not None:
        current_user.city = profile_update.city
    if profile_update.state is not None:
        current_user.state = profile_update.state
    if profile_update.landmark is not None:
        current_user.landmark = profile_update.landmark

    db.commit()
    db.refresh(current_user)
    response.status_code = status.HTTP_200_OK
    return ApiResponse(
        success=True,
        status_code=200,
        message="Profile updated successfully",
        data=UserResponse.model_validate(current_user)
    )
