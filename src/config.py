import os
from dotenv import load_dotenv

load_dotenv()

port: int = int(os.getenv("PORT", 4000))

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password123@localhost:5432/darwin_box_db"
)