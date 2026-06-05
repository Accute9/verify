from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .llm import evaluate_claim
from .whisper_model import transcribe_audio
import json
import asyncio
import os
import traceback
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
    CHUNK_THRESHOLD = 5
    await websocket.accept()
    print("WebSocket connection accepted")

    buffer = bytearray()
    chunk_count = 0
    webm_header = None
    first_batch = True

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    output_folder = os.path.join(BASE_DIR, "temp")
    os.makedirs(output_folder, exist_ok=True)
    send_lock = asyncio.Lock() # ensure only one send_text at a time

    async def send_message_threadsafe(message: str):
        async with send_lock:
            try:
                await websocket.send_text(message)
            except Exception as e:
                print(f"Error sending message: {e}")

    async def keep_alive():
        while True:
            await asyncio.sleep(10)
            await send_message_threadsafe(json.dumps({"status": "keep-alive ping"}))

    asyncio.create_task(keep_alive())

    async def transcribe_and_send(websocket: WebSocket, audio_data: bytes, file_path: str):
        try:
            loop = asyncio.get_running_loop()
            transcription = await loop.run_in_executor(None, transcribe_audio, file_path)
            print(f"Transcription: {transcription}")
            await send_message_threadsafe(json.dumps({"transcription": transcription}))
        except Exception as e:
            print(f"Transcription error: {e}")
            traceback.print_exc()
            try:
                await send_message_threadsafe(json.dumps({"error": f"Transcription error: {str(e)}"}))
            except Exception as e:
                print(f"Failed to send error message to client: {e}")

    try:
        while True: 
            print("Waiting for data...")
            data = await websocket.receive_bytes()
            # MediaRecorder omits header for every batch after first
            if webm_header is None:
                webm_header = bytes(data) # webm header must contain data of first batch
            buffer.extend(data)
            chunk_count += 1
            print(f"Chunk received: {len(data)} bytes, total buffer size: {len(buffer)} bytes, chunk count: {chunk_count}")
            # client has been timing out waiting for response, so send confirmation response
            # await send_queue.put(json.dumps({"status": "chunk received", "chunk_count": chunk_count}))
            # wait websocket.send_text(json.dumps({"status": "chunk received", "chunk_count": chunk_count}))
            if chunk_count >= CHUNK_THRESHOLD:
                if first_batch:
                    audio_data = bytes(buffer)
                    first_batch = False
                else:
                    audio_data = webm_header + bytes(buffer)
                buffer.clear()
                chunk_count = 0
                print(f"Processing batch: {len(audio_data)} bytes")
                file_path = os.path.join(output_folder, f"{uuid.uuid4()}.webm")
                with open(file_path, "wb") as f:
                    f.write(audio_data)
                print(f"File written: {file_path}")
                # try:
                asyncio.create_task(transcribe_and_send(websocket, audio_data, file_path))
                # except Exception as e:
                #     print(f"Transcription error: {e}")
                #     try:
                #         await send_message_threadsafe(json.dumps({"error": f"Transcription error: {str(e)}"}))
                #     except Exception:
                #         print("Failed to send error message to client")
    except WebSocketDisconnect:
        print("WebSocket disconnected")
        traceback.print_exc()
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        traceback.print_exc()

 

