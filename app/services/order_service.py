"""
Order service layer containing business logic for order operations.
Handles order creation, retrieval, and inventory management.
"""
from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
import logging

from app.database.connection import get_database
from app.models.order import OrderCreate, OrderDetails, OrderItemResponse
from app.services.product_service import product_service

logger = logging.getLogger(__name__)


class OrderService:
    """Service class for order-related business operations."""
    
    def __init__(self):
        self.collection_name = "orders"
    
    async def create_order(self, order_data: OrderCreate) -> str:
        """
        Create a new order with inventory validation and management.
        
        Args:
            order_data: Order creation data
            
        Returns:
            str: Created order ID
            
        Raises:
            Exception: If order creation fails or products unavailable
        """
        try:
            db = get_database()
            collection = db[self.collection_name]
            
            # Validate products and calculate total
            order_total = 0.0
            validated_items = []
            
            for item in order_data.items:
                # Check product availability and get price
                available, price = await product_service.check_product_availability(
                    item.productId, item.qty
                )
                
                if not available:
                    raise Exception(f"Product {item.productId} is not available or insufficient quantity")
                
                validated_items.append({
                    "productId": item.productId,
                    "qty": item.qty,
                    "price": price
                })
                
                order_total += price * item.qty
            
            # Create order document
            order_doc = {
                "userId": order_data.userId,
                "items": [{"productId": item["productId"], "qty": item["qty"]} for item in validated_items],
                "total": order_total,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Insert order
            result = collection.insert_one(order_doc)
            order_id = str(result.inserted_id)
            
            # Update inventory for each product
            # Note: In production, this should be done in a transaction
            for item in validated_items:
                # For simplicity, we'll assume first available size is used
                product = await product_service.get_product_by_id(item["productId"])
                if product:
                    # Find first available size with enough quantity
                    for size in product.sizes:
                        if size.quantity >= item["qty"]:
                            await product_service.update_product_inventory(
                                item["productId"], size.size, item["qty"]
                            )
                            break
            
            logger.info(f"Created order with ID: {order_id}")
            return order_id
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise Exception(f"Failed to create order: {str(e)}")
    
    async def get_user_orders(
        self, 
        user_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Retrieve orders for a specific user with pagination.
        
        Args:
            user_id: User identifier
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            Dict containing orders and pagination info
        """
        try:
            db = get_database()
            collection = db[self.collection_name]
            
            # Build query filter for user
            query_filter = {"userId": user_id}
            
            # Get total count for pagination
            total_count = await collection.count_documents(query_filter)
            
            # Fetch orders with pagination, sorted by creation date (newest first)
            cursor = collection.find(query_filter).sort("created_at", -1).skip(offset).limit(limit)
            orders = await cursor.to_list(length=limit)
            
            # Transform to response format with product details
            order_list = []
            for order in orders:
                order_items = []
                
                for item in order["items"]:
                    # Get product details
                    product = await product_service.get_product_by_id(item["productId"])
                    
                    if product:
                        product_details = {
                            "name": product.name,
                            "id": item["productId"]
                        }
                    else:
                        # Handle case where product might be deleted
                        product_details = {
                            "name": "Product Not Found",
                            "id": item["productId"]
                        }
                    
                    order_items.append(OrderItemResponse(
                        productDetails=product_details,
                        qty=item["qty"]
                    ))
                
                order_list.append(OrderDetails(
                    id=str(order["_id"]),
                    items=order_items,
                    total=order["total"]
                ))
            
            # Calculate pagination info
            next_offset = offset + limit if offset + limit < total_count else None
            previous_offset = max(0, offset - limit) if offset > 0 else None
            
            pagination = {
                "next": next_offset,
                "limit": limit,
                "previous": previous_offset if previous_offset is not None else -limit
            }
            
            return {
                "data": order_list,
                "page": pagination
            }
            
        except Exception as e:
            logger.error(f"Error retrieving orders for user {user_id}: {e}")
            raise Exception(f"Failed to retrieve orders: {str(e)}")
    
    async def get_order_by_id(self, order_id: str) -> Optional[dict]:
        """
        Get an order by its ID.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Order document or None if not found
        """
        try:
            if not ObjectId.is_valid(order_id):
                return None
                
            db = get_database()
            collection = db[self.collection_name]
            
            order_doc = await collection.find_one({"_id": ObjectId(order_id)})
            
            if order_doc:
                order_doc["_id"] = str(order_doc["_id"])
                return order_doc
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving order {order_id}: {e}")
            return None


# Global service instance
order_service = OrderService()