"""
FastAPI Main Application
Natural Language Cross-Platform Data Query RAG Agent
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our custom modules
from routes.query_router import router as query_router
from db.mongodb import MongoDB
from db.mysql import MySQL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database instances
mongodb_client = None
mysql_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global mongodb_client, mysql_client
    
    # Startup
    logger.info("🚀 Starting AI Data Query System...")
    
    # Initialize database connections
    try:
        mongodb_client = MongoDB()
        await mongodb_client.connect()
        logger.info("✅ MongoDB connected successfully")
        
        mysql_client = MySQL()
        await mysql_client.connect()
        logger.info("✅ MySQL connected successfully")
        
        # Store clients in app state
        app.state.mongodb = mongodb_client
        app.state.mysql = mysql_client
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down AI Data Query System...")
    if mongodb_client:
        await mongodb_client.close()
    if mysql_client:
        await mysql_client.close()
    logger.info("✅ Cleanup completed")

# Create FastAPI application
app = FastAPI(
    title=os.getenv("APP_NAME", "AI Data Query System"),
    description="Natural Language Cross-Platform Data Query RAG Agent for Wealth Management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(query_router, prefix="/api/v1", tags=["queries"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": f"{os.getenv('APP_NAME', 'AI Data Query System')} is running! 🚀",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "mongodb": "connected" if mongodb_client else "disconnected",
            "mysql": "connected" if mysql_client else "disconnected"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "true").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
