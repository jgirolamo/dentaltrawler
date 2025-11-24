"""
Run the FastAPI server
"""

import uvicorn
import os
from pathlib import Path

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting Dental Clinic API server...")
    print(f"Server will be available at http://{host}:{port}")
    print(f"API documentation at http://{host}:{port}/docs")
    print(f"Search interface at http://{host}:{port}/")
    
    uvicorn.run(
        "api:app",
        host=host,
        port=port,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )

