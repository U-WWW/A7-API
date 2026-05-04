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

    # 🔥 التعديل العبقري: شلنا شرط الصيغة من الإعدادات عشان نمنع الإيرور نهائياً 🔥
    # 🔥 التمويه الأعمق: الاستغناء عن الكوكيز والويب تماماً 🔥
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'simulate': True, 
        'nocheckcertificate': True,
        # امسح سطر الـ cookiefile خالص من هنا
        'extractor_args': {
            # إجبار يوتيوب يشوفنا كتطبيق موبايل فقط (أيفون وأندرويد) للهروب من اختبار البوت
            'youtube': ['player_client=ios,android'] 
        },
        # إضافة User-Agent بتاع أيفون عشان نكمل التمويه
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            direct_url = None
            file_ext = 'mp4'

            if audio_only:
                # فلترة ذكية للحصول على الصوت فقط (m4a)
                audio_formats = [f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none']
                if audio_formats:
                    best_audio = audio_formats[-1] # yt-dlp بيرتبهم من الأقل للأعلى جودة
                    direct_url = best_audio.get('url')
                    file_ext = best_audio.get('ext', 'm4a')
                else:
                    # لو مفيش صوت بس، نجيب أي رابط فيه صوت كاحتياطي
                    any_audio = [f for f in formats if f.get('acodec') != 'none']
                    if any_audio:
                        direct_url = any_audio[-1].get('url')
                        file_ext = 'm4a'
            else:
                # فلترة للحصول على فيديو مدمج (صوت وصورة مع بعض) عشان يشتغل مباشر
                merged_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('acodec') != 'none']
                if merged_formats:
                    best_video = merged_formats[-1]
                    direct_url = best_video.get('url')
                    file_ext = best_video.get('ext', 'mp4')
                else:
                    direct_url = info.get('url')

            # الاحتياطي الأخير لو الفلترة فشلت
            if not direct_url:
                direct_url = info.get('url')
                
            if not direct_url:
                raise HTTPException(status_code=400, detail="لم نتمكن من استخراج الرابط المباشر من يوتيوب")

            return {
                "success": True,
                "video_id": info.get('id'), 
                "title": info.get('title'),
                "thumbnail": info.get('thumbnail'),
                "duration": info.get('duration'), 
                "direct_url": direct_url, 
                "ext": file_ext
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def home():
    return {"message": "A7 Bulletproof Engine is Running! 🛡️🚀"}
