from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


# ==================== PRODUCT SCHEMAS ====================

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    price: float = Field(..., gt=0)
    description: Optional[str] = None
    image_url: Optional[str] = None
    # New fields
    detail_description: Optional[str] = None
    discount: Optional[float] = Field(default=0.0, ge=0, le=100)
    category_id: Optional[int] = None
    company_id: Optional[int] = None
    color: Optional[str] = Field(None, max_length=100)
    extra_images: Optional[List[str]] = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    category_name: Optional[str] = None  # Derived from category relationship
    company_name: Optional[str] = None  # Derived from company relationship

    model_config = {"from_attributes": True}


# ==================== CATEGORY SCHEMAS ====================

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int

    model_config = {"from_attributes": True}


class CategoryWithProductsResponse(CategoryBase):
    id: int
    products: List[ProductResponse] = []

    model_config = {"from_attributes": True}


# ==================== COMPANY SCHEMAS ====================

class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    website_url: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int

    model_config = {"from_attributes": True}


class CompanyWithProductsResponse(CompanyBase):
    id: int
    products: List[ProductResponse] = []

    model_config = {"from_attributes": True}


# ==================== USER SCHEMAS ====================

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    confirm_password: str
    city: Optional[str] = None
    state: Optional[str] = None
    landmark: Optional[str] = None

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    city: Optional[str] = None
    state: Optional[str] = None
    landmark: Optional[str] = None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    landmark: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# ==================== CART SCHEMAS ====================

class CartItemBase(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(default=1, gt=0)


class CartItemCreate(CartItemBase):
    pass


class CartItemResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int

    model_config = {"from_attributes": True}


class CartItemDetailResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    product: ProductResponse

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    """Response for the entire cart of a user"""
    items: List[CartItemDetailResponse]
    total_items: int
    total_price: float
