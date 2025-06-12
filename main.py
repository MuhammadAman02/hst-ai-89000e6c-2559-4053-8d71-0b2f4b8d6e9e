import os
from dotenv import load_dotenv
import uvicorn
from app.main import app

# Load environment variables from .env file (if present)
load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")  # Fly.io expects 0.0.0.0
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,  # Set to False for production
        log_level="info"
    )