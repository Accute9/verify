from fastapi import FastAPI, UploadFile, File, WebSocket
from fastapi.responses import HTMLResponse
from .llm import generate_claim, separate_claim, evaluate_claim
from .search import retrieve_sources
from .whisper_model import transcribe_audio
import json
import websockets
import asyncio
import uuid

app = FastAPI()

@app.get("/")
def index():
    return {"message": "verify is working"}

@app.get("/fact-check")
async def fact_check():
    content = """“Nobody talks about this, but your phone is probably ruining your sleep even if you stop using it before bed. Researchers found that just having your phone in the same room can reduce sleep quality because your brain stays subconsciously alert. That’s why high performers leave their phones outside the bedroom completely. One study even showed people fell asleep faster and had deeper REM sleep after only three nights without a phone nearby.”"""
    evaluation = await evaluate_claim(content)
    return evaluation

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes() # some chunk of audio data from chrome.tabCapture
            with open(f"temp/{uuid.uuid4()}_audio_chunk.wav", "wb") as f:
                f.write(data)
            transcription = asyncio.get_event_loop().run_in_executor(None, transcribe_audio, "temp/audio_chunk.wav")
            return_data = {
                "transcription": transcription,
            }
            await websocket.send_text(json.dumps(return_data))
    except websockets.expcetions.ConnectionClosedError:
        print("WebSocket disconnected unexpectedly")

@app.post("/transcribe")
def transcribe(file: UploadFile = File(...)):
    file_location = f"temp/{file.filename}" # deleted after transcription
 

