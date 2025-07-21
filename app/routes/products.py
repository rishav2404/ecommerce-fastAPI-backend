"""
Product API routes for the e-commerce platform.
Handles product creation and listing with filtering capabilities.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from app.models.product import ProductCreate, ProductResponse, ProductListResponse
from app.services.product_service import product_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(product: ProductCreate):
    """
    Create a new product.
    
    Creates a new product with the specified name, price, and size options.
    Each size includes quantity information for inventory management.
    
    Args:
        product: Product creation data including name, price, and sizes
        
    Returns:
        ProductResponse: Contains the created product ID
        
    Raises:
        HTTPException: 400 if validation fails, 500 if creation fails
    """
    try:
        product_id = await product_service.create_product(product)
        return ProductResponse(id=product_id)
        
    except ValueError as e:
        logger.warning(f"Product validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"Product creation error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=ProductListResponse)
async def list_products(
    name: Optional[str] = Query(None, description="Filter by product name (supports partial matching)"),
    size: Optional[str] = Query(None, description="Filter by available size"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of products to return"),
    offset: int = Query(0, ge=0, description="Number of products to skip")
):
    """
    List products with optional filtering and pagination.
    
    Retrieves a paginated list of products with optional name and size filters.
    Name filtering supports partial matching (case-insensitive).
    Size filtering shows only products with the specified size in stock.
    
    Args:
        name: Optional name filter for partial matching
        size: Optional size filter for available inventory
        limit: Maximum results per page (1-100, default 10)
        offset: Results to skip for pagination (default 0)
        
    Returns:
        ProductListResponse: List of products with pagination info
        
    Raises:
        HTTPException: 500 if retrieval fails
    """
    try:
        result = await product_service.get_products(
            name=name,
            size=size,
            limit=limit,
            offset=offset
        )
        
        return ProductListResponse(**result)
        
    except Exception as e:
        logger.error(f"Product listing error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")