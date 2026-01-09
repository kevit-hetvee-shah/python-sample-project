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


class ApiListResponse(ApiResponse):
    """Standard API response structure for successful list requests."""
    data: List[Any] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "status_code": 200,
                "message": "Success",
                "data": []
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
