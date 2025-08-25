import fastapi
import uvicorn
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
import src.config as config
from src.utils.log import logger
from src.database import create_tables
from src.models import Company, Team, HierarchyLevel, User, Policy, ApprovalStep, Expense, Approval  # Import to register the models
from src.api.api import router

load_dotenv()

@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    """Handle application startup and shutdown events"""
    # Startup
    logger.info("Creating database tables...")
    create_tables()
    logger.info("Database tables created successfully")
    yield
    # Shutdown (if needed)
    logger.info("Application shutting down...")

app = fastapi.FastAPI(
    title="DarwinBox POC - Expense Tracker",
    description="B2B Expense Management with Approval Workflows",
    version="1.0.0",
    lifespan=lifespan
)

# Include API routes
app.include_router(router)

@app.get("/")
async def health():
    return {"status": "healthy", "message": "Expense Tracker API is running"}

if __name__ == "__main__":
    logger.info("Starting the application at port %s", config.port)
    uvicorn.run(app, port=config.port)