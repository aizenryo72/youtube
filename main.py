import datetime
import pytz
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp

app = FastAPI(title="Sukoon Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MOOD_PRESETS = {
    "morning": "morning peaceful bhakti bhajan krishna shiv soothing",
    "afternoon": "bollywood lofi chill beats study relax hindi",
    "evening": "heart touching romantic sad evening songs arijit mohit chauhan",
    "night": "late night deep sukoon acoustic soulful hindi songs"
}

GENRE_QUERIES = {
    "sad": "best sad heart broken bollywood hindi songs",
    "romantic": "top romantic evergreen love songs hindi",
    "bhakti": "peaceful morning aarti bhajan shiv ram krishna",
    "bhojpuri": "smooth sweet melodic bhojpuri songs",
    "funk": "brazilian phonk bass boost gym phonk workout",
    "english": "top global chill english pop acoustic hits",
    "90s": "90s bollywood golden classic superhits",
    "old": "retro vintage golden hits kishore lata rafi mukesh",
    "qawwali": "coke studio classic sufi qawwali rahat nusrat",
    "gym": "high energy gym workout motivation phonk beats"
}

SEARCH_OPTS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'extract_flat': True,
    'skip_download': True
}

def fetch_tracks(search_term: str, limit: int = 15):
    with yt_dlp.YoutubeDL(SEARCH_OPTS) as ydl:
        res = ydl.extract_info(f"ytsearch{limit}:{search_term}", download=False)
        tracks = []
        if 'entries' in res:
            for item in res['entries']:
                if item:
                    tracks.append({
                        "id": item.get("id"),
                        "title": item.get("title"),
                        "artist": item.get("uploader") or "Artist",
                        "duration": item.get("duration") or 0,
                        "thumbnail": f"https://img.youtube.com/vi/{item.get('id')}/hqdefault.jpg"
                    })
        return tracks

@app.get("/api/feed")
def get_feed():
    tz = pytz.timezone('Asia/Kolkata')
    hour = datetime.datetime.now(tz).hour
    
    if 5 <= hour < 11:
        label = "Subah Ka Sukoon ✨ (Bhakti & Calm)"
        preset = MOOD_PRESETS["morning"]
    elif 11 <= hour < 16:
        label = "Dopahar Chill ☕ (Lofi & Focus)"
        preset = MOOD_PRESETS["afternoon"]
    elif 16 <= hour < 21:
        label = "Shaam Ke Nagme 🌇 (Acoustic & Soft)"
        preset = MOOD_PRESETS["evening"]
    else:
        label = "Late Night Sukoon 🌙 (Deep Peaceful Melodies)"
        preset = MOOD_PRESETS["night"]

    tracks = fetch_tracks(preset, limit=12)
    return {
        "greeting": label,
        "tracks": tracks,
        "categories": list(GENRE_QUERIES.keys())
    }

@app.get("/api/category")
def get_by_category(genre: str = Query(...)):
    if genre not in GENRE_QUERIES:
        return {"error": "Invalid Category", "tracks": []}
    tracks = fetch_tracks(GENRE_QUERIES[genre], limit=15)
    return {"category": genre, "tracks": tracks}

@app.get("/api/search")
def search(q: str = Query(...)):
    tracks = fetch_tracks(q, limit=15)
    return {"query": q, "tracks": tracks}

@app.get("/api/stream")
def get_stream(id: str = Query(...)):
    stream_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(stream_opts) as ydl:
        meta = ydl.extract_info(f"https://www.youtube.com/watch?v={id}", download=False)
        return {"stream_url": meta['url']}
