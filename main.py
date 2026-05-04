from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import re

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI(title="A7 Media API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PASSWORD = "A7_VIP_2026"

@app.get("/api/extract")
async def extract_media(url: str, audio_only: bool = False, x_api_key: str = Header(None)):
    
    if x_api_key != API_PASSWORD:
        raise HTTPException(status_code=401, detail="عذراً، الباسورد غير صحيح أو منتهي الصلاحية! ❌")

    target_format = 'bestaudio[ext=m4a]/bestaudio/best' if audio_only else 'best[ext=mp4]/best'

    ydl_opts = {
        'format': target_format,
        'quiet': True,
        'no_warnings': True,
        'simulate': True, 
        'nocheckcertificate': True,
        'cookiefile': 'cookies.txt', # 🔥 السطر السحري: استخدام الكوكيز لاختراق حماية يوتيوب 🔥
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            direct_url = info.get('url')
            
            if not direct_url:
                raise HTTPException(status_code=400, detail="لم نتمكن من استخراج الرابط المباشر")

            return {
                "success": True,
                "video_id": info.get('id'), 
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration'), 
                "direct_url": direct_url, 
                "ext": "m4a" if audio_only else "mp4"
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def home():
    return {"message": "A7 Secured Engine is Running! 🔒🚀"}
