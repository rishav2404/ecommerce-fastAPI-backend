"""
Order data models and validation schemas.
Defines the structure and validation for order-related data.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from bson import ObjectId


class OrderItem(BaseModel):
    """Model for order item information."""

    productId: str = Field(..., description="Product identifier")
    qty: int = Field(..., gt=0, description="Quantity of the product")

    @validator("productId")
    def validate_product_id(cls, v):
        """Validate product ID format."""
        if not v.strip():
            raise ValueError("Product ID cannot be empty")
        return v.strip()


class OrderCreate(BaseModel):
    """Schema for creating a new order."""

    userId: str = Field(..., description="User identifier")
    items: List[OrderItem] = Field(..., min_items=1, description="List of order items")

    @validator("userId")
    def validate_user_id(cls, v):
        """Validate user ID is not empty."""
        if not v.strip():
            raise ValueError("User ID cannot be empty")
        return v.strip()


class OrderResponse(BaseModel):
    """Schema for order creation response."""

    id: str = Field(..., description="Unique order identifier")


class OrderItemResponse(BaseModel):
    """Schema for order item in response."""

    productDetails: dict = Field(..., description="Product information")
    qty: int = Field(..., description="Quantity ordered")


class OrderDetails(BaseModel):
    """Schema for order details in list response."""

    id: str = Field(..., description="Unique order identifier")
    items: List[OrderItemResponse] = Field(
        ..., description="Order items with product details"
    )
    total: float = Field(..., description="Total order amount")


class OrderListResponse(BaseModel):
    """Schema for order list response with pagination."""

    data: List[OrderDetails] = Field(..., description="List of orders")
    page: dict = Field(..., description="Pagination information")


class Order(BaseModel):
    """Complete order model for database storage."""

    id: Optional[str] = Field(alias="_id")
    userId: str
    items: List[OrderItem]
    total: float
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
