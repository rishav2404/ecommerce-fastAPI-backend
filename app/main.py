"""
FastAPI E-commerce Backend Service
Main application entry point with FastAPI setup, middleware, and database connection management.
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from bson import ObjectId
import json
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import uvicorn

from app.config import settings
from app.database.connection import db_manager
from app.routes.products import router as products_router
from app.routes.orders import router as orders_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles database connection setup and cleanup.
    """
    # Startup
    logger.info("Starting FastAPI E-commerce Backend Service")
    try:
        db_manager.connect_to_mongo()
        logger.info("Application startup completed")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    db_manager.close_mongo_connection()
    logger.info("Application shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="E-commerce Backend Service",
    description="A comprehensive FastAPI-based e-commerce backend with MongoDB integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products_router)
app.include_router(orders_router)


@app.get("/", tags=["health"])
async def root():
    """
    Health check endpoint.
    Returns basic application information and status.
    """
    return {
        "message": "E-commerce Backend Service",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs"
    }


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        from bson.timestamp import Timestamp
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, Timestamp):
            return {"t": o.time, "i": o.inc}
        return super().default(o)

@app.get("/health", tags=["health"])
async def health_check():
    """
    Detailed health check endpoint.
    Verifies database connectivity and application status.
    """
    try:
        # Test database connection
        db = db_manager.database
        if db is None:
            raise Exception("Database not connected")
        
        # Ping database
        db_manager.client.admin.command('ping')
        
        result = {
            "status": "healthy",
            "database": "connected",
            "timestamp": db_manager.client.admin.command('isMaster')
        }
        return JSONResponse(content=json.loads(json.dumps(result, cls=JSONEncoder)))
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(status_code=503, content={"detail": f"Service unhealthy: {str(e)}"})


# Custom exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors."""
    logger.warning(f"Validation error: {exc}")
    return HTTPException(status_code=400, detail=str(exc))


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {exc}")
    return HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )