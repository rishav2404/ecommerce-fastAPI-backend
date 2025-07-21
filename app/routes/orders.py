"""
Order API routes for the e-commerce platform.
Handles order creation and user order history retrieval.
"""
from fastapi import APIRouter, HTTPException, Query, Path
import logging

from app.models.order import OrderCreate, OrderResponse, OrderListResponse
from app.services.order_service import order_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(order: OrderCreate):
    """
    Create a new order.
    
    Creates a new order for the specified user with the given items.
    Validates product availability and updates inventory upon successful order creation.
    Calculates the total order amount based on current product prices.
    
    Args:
        order: Order creation data including user ID and items
        
    Returns:
        OrderResponse: Contains the created order ID
        
    Raises:
        HTTPException: 400 if validation fails or products unavailable, 500 if creation fails
    """
    try:
        order_id = await order_service.create_order(order)
        return OrderResponse(id=order_id)
        
    except ValueError as e:
        logger.warning(f"Order validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"Order creation error: {e}")
        if "not available" in str(e) or "insufficient quantity" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{user_id}", response_model=OrderListResponse)
async def get_user_orders(
    user_id: str = Path(..., description="User identifier"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of orders to return"),
    offset: int = Query(0, ge=0, description="Number of orders to skip")
):
    """
    Get orders for a specific user.
    
    Retrieves a paginated list of orders for the specified user, including
    product details for each order item and calculated totals.
    Orders are returned in descending order by creation date (newest first).
    
    Args:
        user_id: User identifier to retrieve orders for
        limit: Maximum results per page (1-100, default 10)
        offset: Results to skip for pagination (default 0)
        
    Returns:
        OrderListResponse: List of user orders with pagination info
        
    Raises:
        HTTPException: 400 if user_id is invalid, 500 if retrieval fails
    """
    try:
        if not user_id.strip():
            raise HTTPException(status_code=400, detail="User ID cannot be empty")
        
        result = await order_service.get_user_orders(
            user_id=user_id.strip(),
            limit=limit,
            offset=offset
        )
        
        return OrderListResponse(**result)
        
    except HTTPException:
        raise
        
    except Exception as e:
        logger.error(f"Order retrieval error for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")