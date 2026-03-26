"""
Rigel Neural Voice Server — Edge TTS FastAPI Backend
Hosted on Render.com (Free Tier) or locally for dev.
Provides /tts endpoint that returns MP3 audio from Edge TTS.
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import edge_tts
import io

app = FastAPI(title="Rigel TTS Server", version="1.0.0")

# Allow all origins for Cloudflare Pages / local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Default voice: Indian-English (Perfect for Gen-Z Hinglish)
DEFAULT_VOICE = "en-IN-NeerjaNeural"

@app.get("/")
async def root():
    return {"status": "online", "server": "Rigel Neural Voice Server", "version": "1.1.0"}

@app.get("/tts")
async def tts(
    text: str = Query(..., description="Text to synthesize"),
    voice: str = Query(DEFAULT_VOICE, description="Edge TTS voice name"),
    rate: str = Query("+55%", description="Speech rate adjustment"),
    pitch: str = Query("+30Hz", description="Pitch adjustment"),
):
    """
    Generate TTS audio from text using Microsoft Edge TTS.
    Streams MP3 audio chunks continuously in real-time.
    """
    async def audio_stream_generator():
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]

    return StreamingResponse(
        audio_stream_generator(),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "inline; filename=rigel_voice.mp3",
            "Cache-Control": "no-cache",
        },
    )

@app.get("/voices")
async def list_voices():
    """List all available Edge TTS voices."""
    voices = await edge_tts.list_voices()
    return voices

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
