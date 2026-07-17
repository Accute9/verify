from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware
from .llm import evaluate_claim
from .whisper_model import transcribe_and_send, flush_remaining_buffer, convert_webm_to_wav
from .database.load_db import store_transcript, generate_bigint_id
import json
import asyncio
import os
import traceback
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://verity.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_origin_regex="http://127.0.0.1:.*",
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def index():
    return {"message": "verify is working"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    CHUNK_THRESHOLD = 10
    await websocket.accept()
    print("WebSocket connection accepted")

    buffer = bytearray()
    chunk_count = 0
    webm_header = b""
    first_batch = True

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    output_folder = os.path.join(BASE_DIR, "temp")
    os.makedirs(output_folder, exist_ok=True)
    send_lock = asyncio.Lock() # ensure only one send_text at a time
    
    async def fact_check_endpoint(transcript_parts: list, id: int):
        content = " ".join(transcript_parts)
        store_transcript(content, id)  # Store the final transcript in the database
        eval_result = await evaluate_claim(content, id)
        
        return eval_result

    async def send_message_threadsafe(message: str):
        async with send_lock:
            if websocket.client_state != WebSocketState.CONNECTED:
                return
            try:
                await websocket.send_text(message)
            except Exception as e:
                print(f"Error sending message: {e}")

    async def keep_alive():
        while True:
            await asyncio.sleep(10)
            await send_message_threadsafe(json.dumps({"status": "keep-alive ping"}))

    keep_alive_task = asyncio.create_task(keep_alive())
    transcription_tasks = set() # track tasks from transcription stuff ya feel
    transcript_parts = []

    try:
        while True:
            print("Waiting for data...")
            message = await websocket.receive()
            if message["type"] == "websocket.disconnect":
                raise WebSocketDisconnect(message.get("code", 1000))
            # check stop signal
            if "text" in message:
                try:
                    payload = json.loads(message["text"])
                except json.JSONDecodeError:
                    continue
                if payload.get("action") == "stop":
                    # Send transcript to fact-checking endpoint
                    print("Stop signal received from client")
                    await flush_remaining_buffer(transcript_parts, buffer, webm_header, send_message_threadsafe)
                    if transcription_tasks:
                        await asyncio.gather(*transcription_tasks, return_exceptions=True) # wait for all transcription tasks to finish
                    await send_message_threadsafe(json.dumps({"final_transcript": " ".join(transcript_parts)})) # send final transcript to client
                    transcript_id = generate_bigint_id()  # Generate a unique ID for this transcript
                    # store_transcript(" ".join(transcript_parts), transcript_id)  # Store the final transcript in the database
                    eval_result = await fact_check_endpoint(transcript_parts, transcript_id)
                    await send_message_threadsafe(json.dumps({"eval_result": eval_result})) # send evaluation result to client
                    keep_alive_task.cancel() # stop keep-alive pings
                    await websocket.close()
                    break
                continue
            data = message.get("bytes")
            if data is None:
                continue
            # MediaRecorder omits header for every batch after first
            if webm_header == b"": # if empty byte object, this is the first batch and contains header
                # webm_header = bytes(data) # webm header must contain data of first batch
                cluster_marker = bytes([0x1F, 0x43, 0xB6, 0x75]) # start of cluster in webm
                cluster_index = bytes(data).find(cluster_marker)
                webm_header = bytes(data[:cluster_index]) if cluster_index != -1 else webm_header
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
                wav_path = convert_webm_to_wav(file_path)
                # try:
                transcription_task = asyncio.create_task(transcribe_and_send(transcript_parts, wav_path, send_message_threadsafe))
                transcription_task.add_done_callback(transcription_tasks.discard) # remove from set when done
                transcription_tasks.add(transcription_task)
    except WebSocketDisconnect:
        print("WebSocket disconnected")
        # traceback.print_exc() - for debugging purposes
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        traceback.print_exc()
    finally:
        keep_alive_task.cancel()
        for task in transcription_tasks:
            task.cancel()


 

