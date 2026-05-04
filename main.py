from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import re

app = FastAPI(title="A7 Media API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 الباسورد السري بتاعك (غيره براحتك من هنا ووزعه للمستخدمين) 🔥
API_PASSWORD = "2026"

@app.get("/api/extract")
async def extract_media(url: str, audio_only: bool = False, x_api_key: str = Header(None)):
    
    # 1. التحقق من الباسورد
    if x_api_key != API_PASSWORD:
        raise HTTPException(status_code=401, detail="عذراً، الباسورد غير صحيح أو منتهي الصلاحية! ❌")

    # 2. إعدادات استخراج الرابط المباشر
    target_format = 'bestaudio[ext=m4a]/bestaudio/best' if audio_only else 'best[ext=mp4]/best'

    ydl_opts = {
        'format': target_format,
        'quiet': True,
        'no_warnings': True,
        'simulate': True, 
        'nocheckcertificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            direct_url = info.get('url')
            
            if not direct_url:
                raise HTTPException(status_code=400, detail="لم نتمكن من استخراج الرابط المباشر")

            return {
                "success": True,
                "video_id": info.get('id'), # 🎯 مهم جداً عشان نشغل الـ Embed في فلاتر
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