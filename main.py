import os
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file (if present)
load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")  # Fly.io expects 0.0.0.0
    
    print(f"🚀 Starting Minecraft Clone Server on {host}:{port}")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,  # Set to False for production
        log_level="info"
    )