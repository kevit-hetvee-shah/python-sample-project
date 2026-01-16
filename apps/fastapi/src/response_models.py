from typing import Generic, TypeVar, Optional, Any, Union, List
from pydantic import BaseModel, Field

T = TypeVar('T')


class ApiResponse(BaseModel):
    """Standard API response structure for successful requests."""
    success: bool = True
    status_code: int
    message: str
    data: Optional[Any] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "status_code": 200,
                "message": "Success",
                "data": {}
            }
        }


class PaginationData(BaseModel):
    """Pagination metadata for list responses."""
    page: int
    page_size: int
    total: int
    total_pages: int


class PaginatedListResponse(BaseModel):
    """Paginated list data structure."""
    items: List[Any]
    pagination: PaginationData


class ApiListResponse(ApiResponse):
    """Standard API response structure for successful list requests."""
    data: PaginatedListResponse

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "status_code": 200,
                "message": "Success",
                "data": {
                    "items": [],
                    "pagination": {
                        "page": 1,
                        "page_size": 10,
                        "total": 100,
                        "total_pages": 10
                    }
                }
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response structure."""
    success: bool = False
    status_code: int
    message: str
    details: Optional[Union[str, dict, list]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "status_code": 400,
                "message": "Error occurred",
                "details": {}
            }
        }
