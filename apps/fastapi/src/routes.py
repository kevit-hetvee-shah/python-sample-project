from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List

from apps.fastapi.src.models import get_db, Product, User, Cart, Category, Company
from apps.fastapi.src.schemas import (
    ProductCreate, ProductResponse, UserRegister, UserLogin,
    UserResponse, UserUpdate, TokenResponse, CartItemCreate,
    CartItemResponse, CartItemDetailResponse, CartResponse,
    CategoryResponse, CompanyResponse, CategoryWithProductsResponse,
    CompanyWithProductsResponse
)
from apps.fastapi.src.auth import (
    get_current_user, authenticate_user, create_access_token,
    get_password_hash
)
from apps.fastapi.src.response_models import ApiResponse, ApiListResponse, ErrorResponse, PaginationData, PaginatedListResponse

router = APIRouter()

# ==================== USER ROUTES ====================

@router.get("/users", tags=["Users"])
def list_users(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    List all users with id, username, city, state, and landmark.
    Supports pagination with page and page_size parameters.
    """
    # Calculate skip offset
    skip = (page - 1) * page_size

    # Get total count
    total = db.query(User).count()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size

    # Get paginated users
    users = db.query(User).offset(skip).limit(page_size).all()

    response.status_code = status.HTTP_200_OK
    return ApiListResponse(
        success=True,
        status_code=200,
        message="Users retrieved successfully",
        data=PaginatedListResponse(
            items=[UserResponse.model_validate(u) for u in users],
            pagination=PaginationData(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages
            )
        )
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
def list_products(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    List all products with id, name, price, description, and image_url.
    Supports pagination with page and page_size parameters.
    """
    # Calculate skip offset
    skip = (page - 1) * page_size

    # Get total count
    total = db.query(Product).count()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size

    # Get paginated products
    products = db.query(Product).offset(skip).limit(page_size).all()

    # Build product responses with category and company names
    product_responses = []
    for p in products:
        product_dict = ProductResponse.model_validate(p).model_dump()
        product_dict["category_name"] = p.category.name if p.category else None
        product_dict["company_name"] = p.company.name if p.company else None
        product_responses.append(product_dict)

    response.status_code = status.HTTP_200_OK
    return ApiListResponse(
        success=True,
        status_code=200,
        message="Products retrieved successfully",
        data=PaginatedListResponse(
            items=product_responses,
            pagination=PaginationData(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages
            )
        )
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
    product_dict = ProductResponse.model_validate(product).model_dump()
    product_dict["category_name"] = product.category.name if product.category else None
    product_dict["company_name"] = product.company.name if product.company else None
    return ApiResponse(
        success=True,
        status_code=200,
        message="Product retrieved successfully",
        data=product_dict
    )


# ==================== CATEGORY ROUTES ====================

@router.get("/categories", tags=["Categories"])
def list_categories(
    page: int | None = None,
    page_size: int | None = None,
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    List all categories with id, name, and description.
    By default returns all categories. Use page and page_size for pagination.
    """
    # Get total count
    total = db.query(Category).count()

    # If pagination parameters are provided, return paginated response
    if page is not None and page_size is not None:
        skip = (page - 1) * page_size
        total_pages = (total + page_size - 1) // page_size
        categories = db.query(Category).offset(skip).limit(page_size).all()

        response.status_code = status.HTTP_200_OK
        return ApiListResponse(
            success=True,
            status_code=200,
            message="Categories retrieved successfully",
            data=PaginatedListResponse(
                items=[CategoryResponse.model_validate(c) for c in categories],
                pagination=PaginationData(
                    page=page,
                    page_size=page_size,
                    total=total,
                    total_pages=total_pages
                )
            )
        )
    else:
        # Return all categories with consistent structure
        categories = db.query(Category).all()

        response.status_code = status.HTTP_200_OK
        return ApiListResponse(
            success=True,
            status_code=200,
            message="Categories retrieved successfully",
            data=PaginatedListResponse(
                items=[CategoryResponse.model_validate(c) for c in categories],
                pagination=PaginationData(
                    page=1,
                    page_size=total,
                    total=total,
                    total_pages=1
                )
            )
        )


@router.get("/categories/{category_id}", tags=["Categories"])
def get_category(category_id: int, db: Session = Depends(get_db), response: Response = None):
    """
    Get a specific category by ID with its products.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(
            success=False,
            status_code=404,
            message=f"Category with id {category_id} not found",
            details={"category_id": category_id}
        )

    # Get products with category and company names
    products = db.query(Product).filter(Product.category_id == category_id).all()
    product_responses = []
    for p in products:
        product_dict = ProductResponse.model_validate(p).model_dump()
        product_dict["category_name"] = p.category.name if p.category else None
        product_dict["company_name"] = p.company.name if p.company else None
        product_responses.append(product_dict)

    response.status_code = status.HTTP_200_OK
    return ApiResponse(
        success=True,
        status_code=200,
        message="Category retrieved successfully",
        data={
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "products": product_responses
        }
    )


# ==================== COMPANY ROUTES ====================

@router.get("/companies", tags=["Companies"])
def list_companies(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    List all companies with id, name, description, website_url, and logo_url.
    Supports pagination with page and page_size parameters.
    """
    # Calculate skip offset
    skip = (page - 1) * page_size

    # Get total count
    total = db.query(Company).count()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size

    # Get paginated companies
    companies = db.query(Company).offset(skip).limit(page_size).all()

    response.status_code = status.HTTP_200_OK
    return ApiListResponse(
        success=True,
        status_code=200,
        message="Companies retrieved successfully",
        data=PaginatedListResponse(
            items=[CompanyResponse.model_validate(c) for c in companies],
            pagination=PaginationData(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages
            )
        )
    )


@router.get("/companies/{company_id}", tags=["Companies"])
def get_company(company_id: int, db: Session = Depends(get_db), response: Response = None):
    """
    Get a specific company by ID with its products.
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(
            success=False,
            status_code=404,
            message=f"Company with id {company_id} not found",
            details={"company_id": company_id}
        )

    # Get products with category and company names
    products = db.query(Product).filter(Product.company_id == company_id).all()
    product_responses = []
    for p in products:
        product_dict = ProductResponse.model_validate(p).model_dump()
        product_dict["category_name"] = p.category.name if p.category else None
        product_dict["company_name"] = p.company.name if p.company else None
        product_responses.append(product_dict)

    response.status_code = status.HTTP_200_OK
    return ApiResponse(
        success=True,
        status_code=200,
        message="Company retrieved successfully",
        data={
            "id": company.id,
            "name": company.name,
            "description": company.description,
            "website_url": company.website_url,
            "logo_url": company.logo_url,
            "products": product_responses
        }
    )


# ==================== PRODUCT FILTERING ROUTES ====================

@router.get("/products/by-company/{company_id}", tags=["Products"])
def get_products_by_company(
    company_id: int,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    Get all products for a given company by company ID with pagination.
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(
            success=False,
            status_code=404,
            message=f"Company with id {company_id} not found",
            details={"company_id": company_id}
        )

    # Calculate skip offset
    skip = (page - 1) * page_size

    # Get total count for this company's products
    total = db.query(Product).filter(Product.company_id == company_id).count()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size

    # Get paginated products
    products = db.query(Product).filter(Product.company_id == company_id).offset(skip).limit(page_size).all()

    response.status_code = status.HTTP_200_OK
    product_responses = []
    for p in products:
        product_dict = ProductResponse.model_validate(p).model_dump()
        product_dict["category_name"] = p.category.name if p.category else None
        product_dict["company_name"] = p.company.name if p.company else None
        product_responses.append(product_dict)
    return ApiListResponse(
        success=True,
        status_code=200,
        message=f"Products for company '{company.name}' retrieved successfully",
        data=PaginatedListResponse(
            items=product_responses,
            pagination=PaginationData(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages
            )
        )
    )


@router.get("/products/by-category/{category_id}", tags=["Products"])
def get_products_by_category(
    category_id: int,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    Get all products for a given category by category ID with pagination.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(
            success=False,
            status_code=404,
            message=f"Category with id {category_id} not found",
            details={"category_id": category_id}
        )

    # Calculate skip offset
    skip = (page - 1) * page_size

    # Get total count for this category's products
    total = db.query(Product).filter(Product.category_id == category_id).count()

    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size

    # Get paginated products
    products = db.query(Product).filter(Product.category_id == category_id).offset(skip).limit(page_size).all()

    response.status_code = status.HTTP_200_OK
    product_responses = []
    for p in products:
        product_dict = ProductResponse.model_validate(p).model_dump()
        product_dict["category_name"] = p.category.name if p.category else None
        product_dict["company_name"] = p.company.name if p.company else None
        product_responses.append(product_dict)
    return ApiListResponse(
        success=True,
        status_code=200,
        message=f"Products for category '{category.name}' retrieved successfully",
        data=PaginatedListResponse(
            items=product_responses,
            pagination=PaginationData(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages
            )
        )
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


# ==================== CART ROUTES ====================

@router.get("/cart", tags=["Cart"])
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    Get all items in the current user's cart.
    Requires JWT authentication.
    """
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()

    items_with_products = []
    total_items = 0
    total_price = 0.0

    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            item_detail = CartItemDetailResponse(
                id=item.id,
                user_id=item.user_id,
                product_id=item.product_id,
                quantity=item.quantity,
                product=ProductResponse.model_validate(product)
            )
            items_with_products.append(item_detail)
            total_items += item.quantity
            total_price += product.price * item.quantity

    response.status_code = status.HTTP_200_OK
    return ApiResponse(
        success=True,
        status_code=200,
        message="Cart retrieved successfully",
        data={
            "items": items_with_products,
            "total_items": total_items,
            "total_price": round(total_price, 2)
        }
    )


@router.post("/cart", tags=["Cart"])
def add_to_cart(
    cart_item: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    Add a product to the current user's cart.
    Requires JWT authentication.
    If product already exists in cart, updates quantity.
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(
            success=False,
            status_code=404,
            message=f"Product with id {cart_item.product_id} not found",
            details={"product_id": cart_item.product_id}
        )

    # Check if item already exists in cart
    existing_item = db.query(Cart).filter(
        Cart.user_id == current_user.id,
        Cart.product_id == cart_item.product_id
    ).first()

    if existing_item:
        # Update quantity
        existing_item.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing_item)
        response.status_code = status.HTTP_200_OK
        return ApiResponse(
            success=True,
            status_code=200,
            message="Cart item quantity updated",
            data=CartItemResponse.model_validate(existing_item)
        )
    else:
        # Add new item to cart
        new_cart_item = Cart(
            user_id=current_user.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        db.add(new_cart_item)
        db.commit()
        db.refresh(new_cart_item)
        response.status_code = status.HTTP_201_CREATED
        return ApiResponse(
            success=True,
            status_code=201,
            message="Item added to cart",
            data=CartItemResponse.model_validate(new_cart_item)
        )


@router.delete("/cart/{cart_item_id}", tags=["Cart"])
def remove_from_cart(
    cart_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    Remove an item from the current user's cart by cart item ID.
    Requires JWT authentication.
    """
    cart_item = db.query(Cart).filter(
        Cart.id == cart_item_id,
        Cart.user_id == current_user.id
    ).first()

    if not cart_item:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(
            success=False,
            status_code=404,
            message=f"Cart item with id {cart_item_id} not found",
            details={"cart_item_id": cart_item_id}
        )

    db.delete(cart_item)
    db.commit()
    response.status_code = status.HTTP_200_OK
    return ApiResponse(
        success=True,
        status_code=200,
        message="Item removed from cart",
        data=None
    )


@router.put("/cart/{cart_item_id}", tags=["Cart"])
def update_cart_item_quantity(
    cart_item_id: int,
    quantity: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    Update the quantity of an item in the current user's cart.
    Requires JWT authentication.
    Set quantity to 0 to remove the item.
    """
    if quantity < 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return ErrorResponse(
            success=False,
            status_code=400,
            message="Quantity cannot be negative",
            details={"quantity": quantity}
        )

    cart_item = db.query(Cart).filter(
        Cart.id == cart_item_id,
        Cart.user_id == current_user.id
    ).first()

    if not cart_item:
        response.status_code = status.HTTP_404_NOT_FOUND
        return ErrorResponse(
            success=False,
            status_code=404,
            message=f"Cart item with id {cart_item_id} not found",
            details={"cart_item_id": cart_item_id}
        )

    if quantity == 0:
        db.delete(cart_item)
        db.commit()
        response.status_code = status.HTTP_200_OK
        return ApiResponse(
            success=True,
            status_code=200,
            message="Item removed from cart (quantity set to 0)",
            data=None
        )

    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    response.status_code = status.HTTP_200_OK
    return ApiResponse(
        success=True,
        status_code=200,
        message="Cart item quantity updated",
        data=CartItemResponse.model_validate(cart_item)
    )


@router.delete("/cart", tags=["Cart"])
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    response: Response = None
):
    """
    Clear all items from the current user's cart.
    Requires JWT authentication.
    """
    cart_items = db.query(Cart).filter(Cart.user_id == current_user.id).all()
    for item in cart_items:
        db.delete(item)
    db.commit()
    response.status_code = status.HTTP_200_OK
    return ApiResponse(
        success=True,
        status_code=200,
        message="Cart cleared successfully",
        data=None
    )
