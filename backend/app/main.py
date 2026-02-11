import logging
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .database import database
# from .celery_app import celery_app

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown events.
    
    - Connect to MongoDB on startup
    - Close MongoDB connection on shutdown
    """
    try:
        # Connect to database on startup
        await database.connect()
        logger.info("Database connection established")
        
        yield
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    finally:
        # Ensure database connection is closed
        await database.close()
        logger.info("Database connection closed")

# Create FastAPI application with lifespan management
app = FastAPI(
    title="RestaurantGrader Backend",
    description="Backend API for restaurant website analysis",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Configuration: Allow ALL origins, methods, and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow ALL origins
    allow_credentials=True,     # Allow cookies/auth
    allow_methods=["*"],        # Allow ALL HTTP methods
    allow_headers=["*"],        # Allow ALL headers
)

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Simple health check endpoint to verify application is running.
    
    Returns:
        dict: Status of the application
    """
    try:
        logger.info("Health check endpoint called")
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "timestamp": str(datetime.now())
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to catch and log unhandled exceptions.
    
    Args:
        request: The incoming request
        exc: The unhandled exception
    
    Returns:
        JSONResponse with error details
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc)
        }
    )

# Import and register routes
from .routes import restaurants, scans, leads

# Register routes with appropriate prefixes
app.include_router(restaurants.router, prefix="/api/restaurants", tags=["restaurants"])
app.include_router(scans.router, prefix="/api/scans", tags=["scans"])
app.include_router(leads.router, prefix="/api/leads", tags=["leads"])

# Run the application if this file is executed directly
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.ENVIRONMENT == "development"
    )