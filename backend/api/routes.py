from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .llm import evaluate_claim
from .whisper_model import transcribe_audio
import json
import asyncio
import os
import wave
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_origin_regex="http://127.0.0.1:.*",
    allow_methods=["*"],
    allow_headers=["*"]
)

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
    CHUNK_THRESHOLD = 10
    await websocket.accept()
    print("WebSocket connection accepted")
    buffer = bytearray()
    chunk_count = 0
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    output_folder = os.path.join(BASE_DIR, "temp")
    os.makedirs(output_folder, exist_ok=True)
    try:
        while True:
            print("Waiting for data...")
            data = await websocket.receive_bytes()
            buffer.extend(data)
            chunk_count += 1
            print(f"Chunk received: {len(data)} bytes, total buffer size: {len(buffer)} bytes, chunk count: {chunk_count}")
            # client has been timing out waiting for response, so send confirmation response
            # await websocket.send_text(json.dumps({"status": "chunk received", "chunk_count": chunk_count}))
            await websocket.send_text(json.dumps({"status": "chunk received", "chunk_count": chunk_count}))
            if chunk_count >= CHUNK_THRESHOLD:
                audio_data = bytes(buffer)
                buffer.clear()
                chunk_count = 0
                print(f"DATA RECEIVED: {len(data)} bytes")
                file_path = os.path.join(output_folder, f"{uuid.uuid4()}.webm")
                with open(file_path, "wb") as f:
                    f.write(audio_data)
                print(f"File written: {file_path}")
                try:
                    transcription = await asyncio.get_running_loop().run_in_executor(
                        None, transcribe_audio, file_path
                    )
                    print(f"Transcription: {transcription}")
                    await websocket.send_text(json.dumps({"transcription": transcription}))
                except Exception as e:
                    print(f"Transcription error: {e}")
                    await websocket.send_text(json.dumps({"error": str(e)}))
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")

# @app.post("/transcribe")
# def transcribe(file: UploadFile = File(...)):
#     file_location = f"temp/{file.filename}" # deleted after transcription
 

