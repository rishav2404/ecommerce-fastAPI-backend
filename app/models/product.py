"""
Product data models and validation schemas.
Defines the structure and validation for product-related data.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from bson import ObjectId


class ProductSize(BaseModel):
    """Model for product size and quantity information."""

    size: str = Field(..., description="Size identifier (e.g., 'S', 'M', 'L', '42')")
    quantity: int = Field(..., ge=0, description="Available quantity for this size")

    @validator("size")
    def validate_size(cls, v):
        """Validate size field is not empty."""
        if not v.strip():
            raise ValueError("Size cannot be empty")
        return v.strip()


class ProductCreate(BaseModel):
    """Schema for creating a new product."""

    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    price: float = Field(..., gt=0, description="Product price (must be positive)")
    sizes: List[ProductSize] = Field(
        ..., min_items=1, description="Available sizes and quantities"
    )

    @validator("name")
    def validate_name(cls, v):
        """Validate product name is not empty."""
        if not v.strip():
            raise ValueError("Product name cannot be empty")
        return v.strip()

    @validator("sizes")
    def validate_sizes(cls, v):
        """Validate sizes list and ensure no duplicate sizes."""
        if not v:
            raise ValueError("At least one size must be specified")

        # Check for duplicate sizes
        sizes_seen = set()
        for size_item in v:
            if size_item.size in sizes_seen:
                raise ValueError(f"Duplicate size: {size_item.size}")
            sizes_seen.add(size_item.size)

        return v


class ProductResponse(BaseModel):
    """Schema for product creation response."""

    id: str = Field(..., description="Unique product identifier")


class ProductListItem(BaseModel):
    """Schema for product list items."""

    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    price: float = Field(..., description="Product price")


class ProductListResponse(BaseModel):
    """Schema for product list response with pagination."""

    data: List[ProductListItem] = Field(..., description="List of products")
    page: dict = Field(..., description="Pagination information")


class Product(BaseModel):
    """Complete product model for database storage."""

    id: Optional[str] = Field(alias="_id")
    name: str
    price: float
    sizes: List[ProductSize]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
