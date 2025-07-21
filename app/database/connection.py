"""
MongoDB database connection management using the PyMongo Async API.
Provides connection setup and database access functionality.
"""

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import certifi
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MongoDB database connections and operations."""

    def __init__(self):
        self.client: MongoClient = None
        self.database = None

    def connect_to_mongo(self):
        """Create database connection."""
        try:
            # self.client = MongoClient(
            #     settings.mongodb_url, server_api=ServerApi("1")
            # )
            self.client = MongoClient(
                settings.mongodb_url,
                server_api=ServerApi("1"),
                tlsCAFile=certifi.where()
            )
            self.database = self.client[settings.database_name]

            # Test the connection
            self.client.admin.command("ping")
            logger.info(
                f"Successfully connected to MongoDB Atlas: {settings.database_name}"
            )

            # Create indexes for better performance
            self._create_indexes()
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def close_mongo_connection(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    def _create_indexes(self):
        """Create database indexes for optimal query performance."""
        try:
            products = self.database.products
            products.create_index("name")
            products.create_index("sizes.size")

            orders = self.database.orders
            orders.create_index("userId")
            orders.create_index("createdAt")

            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Error creating indexes: {e}")


# Global database manager instance
db_manager = DatabaseManager()


def get_database():
    """Get the database instance."""
    return db_manager.database
