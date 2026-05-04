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

    # 🔥 التعديل هنا: تبسيط الطلب عشان يوتيوب ميعترضش (أحسن صوت أو أحسن فيديو مدمج)
    target_format = 'bestaudio' if audio_only else 'best'

    ydl_opts = {
        'format': target_format,
        'quiet': True,
        'no_warnings': True,
        'simulate': True, 
        'nocheckcertificate': True,
        'cookiefile': 'cookies.txt', 
        'extractor_args': {
            'youtube': ['player_client=android,web']
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            direct_url = info.get('url')
            
            # بحث احتياطي لو الرابط المباشر مستخبي
            if not direct_url and 'formats' in info:
                formats = info['formats']
                if audio_only:
                    audio_formats = [f for f in formats if f.get('vcodec') == 'none']
                    if audio_formats:
                        direct_url = audio_formats[-1].get('url')
                else:
                    direct_url = formats[-1].get('url')

            if not direct_url:
                raise HTTPException(status_code=400, detail="لم نتمكن من استخراج الرابط المباشر")

            return {
                "success": True,
                "video_id": info.get('id'), 
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration'), 
                "direct_url": direct_url, 
                # 🔥 هنجيب الصيغة الحقيقية اللي يوتيوب بعتها (سواء m4a أو webm أو mp4)
                "ext": info.get('ext', 'mp3' if audio_only else 'mp4') 
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def home():
    return {"message": "A7 Secured Engine is Running! 🔒🚀"}
