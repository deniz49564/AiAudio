import os
import base64
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google API anahtarını environment variable'dan al
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

class GenerateMusicRequest(BaseModel):
    prompt: str

@app.post("/api/generate-music")
async def generate_music(request: GenerateMusicRequest):
    if not GOOGLE_API_KEY:
        raise HTTPException(status_code=500, detail="Google API anahtarı eksik!")
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/lyria-3-clip-preview:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GOOGLE_API_KEY
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": request.prompt
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        # API'den gelen base64 veriyi al
        for part in result.get("candidates", [{}])[0].get("content", {}).get("parts", []):
            if "inlineData" in part:
                audio_data = base64.b64decode(part["inlineData"]["data"])
                return Response(content=audio_data, media_type="audio/mpeg")
        
        raise HTTPException(status_code=500, detail="Müzik oluşturulamadı!")
    
    except Exception as e:
        print(f"Hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health():
    return {"status": "ok"}