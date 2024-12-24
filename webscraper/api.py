from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import subprocess
import os

app = FastAPI()

# Enable CORS for our frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    urls: List[str]
    filename: str

@app.post("/api/scrape")
async def scrape_urls(request: ScrapeRequest):
    try:
        # Ensure we're in the correct directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Build command with proper URL escaping
        urls_args = " ".join([f'--url "{url}"' for url in request.urls])
        command = f'python3 test_scraper.py {urls_args} --output "{request.filename}"'
        
        # Run the scraper with debug logging
        print(f"Executing command: {command}")
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        print(f"STDOUT: {process.stdout}")
        print(f"STDERR: {process.stderr}")
        
        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=process.stderr)
        
        # Return the path to the generated CSV file
        csv_filename = f"{request.filename}.csv"
        if not os.path.exists(csv_filename):
            raise HTTPException(status_code=500, detail="CSV file not generated")
            
        return {"csvUrl": f"/downloads/{csv_filename}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
