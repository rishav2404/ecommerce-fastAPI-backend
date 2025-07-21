"""
Product service layer containing business logic for product operations.
Handles product creation, retrieval, filtering, and inventory management.
"""

from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
import re
import logging

from app.database.connection import get_database
from app.models.product import ProductCreate, ProductListItem, Product

logger = logging.getLogger(__name__)


class ProductService:
    """Service class for product-related business operations."""

    def __init__(self):
        self.collection_name = "products"

    def create_product(self, product_data: ProductCreate) -> str:
        """
        Create a new product in the database.

        Args:
            product_data: Product creation data

        Returns:
            str: Created product ID

        Raises:
            Exception: If product creation fails
        """
        try:
            db = get_database()
            collection = db[self.collection_name]

            # Prepare product document
            product_doc = {
                "name": product_data.name,
                "price": product_data.price,
                "sizes": [size.dict() for size in product_data.sizes],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Insert product
            result = collection.insert_one(product_doc)
            product_id = str(result.inserted_id)

            logger.info(f"Created product with ID: {product_id}")
            return product_id

        except Exception as e:
            logger.error(f"Error creating product: {e}")
            raise Exception(f"Failed to create product: {str(e)}")

    def get_products(
        self,
        name: Optional[str] = None,
        size: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Retrieve products with optional filtering and pagination.

        Args:
            name: Optional name filter (supports partial matching)
            size: Optional size filter
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Dict containing products and pagination info
        """
        try:
            db = get_database()
            collection = db[self.collection_name]

            # Build query filter
            query_filter = {}

            if name:
                # Case-insensitive partial name matching
                query_filter["name"] = {"$regex": re.escape(name), "$options": "i"}

            if size:
                # Filter by available size
                query_filter["sizes"] = {
                    "$elemMatch": {
                        "size": {"$regex": f"^{re.escape(size)}$", "$options": "i"},
                        "quantity": {"$gt": 0},
                    }
                }

            # Get total count for pagination
            total_count = collection.count_documents(query_filter)

            # Fetch products with pagination
            cursor = collection.find(query_filter).skip(offset).limit(limit)
            products = list(cursor)

            # Transform to response format
            product_list = []
            for product in products:
                product_list.append(
                    ProductListItem(
                        id=str(product["_id"]),
                        name=product["name"],
                        price=product["price"],
                    )
                )

            # Calculate pagination info
            next_offset = offset + limit if offset + limit < total_count else None
            previous_offset = max(0, offset - limit) if offset > 0 else None

            pagination = {
                "next": next_offset,
                "limit": limit,
                "previous": previous_offset if previous_offset is not None else -limit,
            }

            return {"data": product_list, "page": pagination}

        except Exception as e:
            logger.error(f"Error retrieving products: {e}")
            raise Exception(f"Failed to retrieve products: {str(e)}")

    async def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """
        Get a product by its ID.

        Args:
            product_id: Product identifier

        Returns:
            Product object or None if not found
        """
        try:
            if not ObjectId.is_valid(product_id):
                return None

            db = get_database()
            collection = db[self.collection_name]

            product_doc = await collection.find_one({"_id": ObjectId(product_id)})

            if product_doc:
                product_doc["_id"] = str(product_doc["_id"])
                return Product(**product_doc)

            return None

        except Exception as e:
            logger.error(f"Error retrieving product {product_id}: {e}")
            return None

    async def update_product_inventory(
        self, product_id: str, size: str, quantity_used: int
    ) -> bool:
        """
        Update product inventory after an order.

        Args:
            product_id: Product identifier
            size: Size to update
            quantity_used: Quantity to subtract from inventory

        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            if not ObjectId.is_valid(product_id):
                return False

            db = get_database()
            collection = db[self.collection_name]

            # Update the specific size quantity
            result = collection.update_one(
                {
                    "_id": ObjectId(product_id),
                    "sizes.size": size,
                    "sizes.quantity": {"$gte": quantity_used},
                },
                {
                    "$inc": {"sizes.$.quantity": -quantity_used},
                    "$set": {"updated_at": datetime.utcnow().isoformat()},
                },
            )

            return result.modified_count > 0

        except Exception as e:
            logger.error(f"Error updating inventory for product {product_id}: {e}")
            return False

    async def check_product_availability(
        self, product_id: str, quantity: int
    ) -> tuple[bool, float]:
        """
        Check if product is available and get its price.

        Args:
            product_id: Product identifier
            quantity: Required quantity

        Returns:
            Tuple of (availability, price)
        """
        try:
            product = await self.get_product_by_id(product_id)
            if not product:
                return False, 0.0

            # Check if any size has enough quantity
            total_available = sum(size.quantity for size in product.sizes)

            if total_available >= quantity:
                return True, product.price

            return False, product.price

        except Exception as e:
            logger.error(f"Error checking availability for product {product_id}: {e}")
            return False, 0.0


# Global service instance
product_service = ProductService()
