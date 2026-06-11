import whisper
import asyncio
import json
import traceback
import os
import uuid
import subprocess

model = whisper.load_model("base")

def transcribe_audio(file_path: str) -> str:
    result = model.transcribe(file_path)
    return result["text"]

def convert_webm_to_wav(file_path: str) -> str:
    output_path = file_path.replace(".webm", ".wav")
    subprocess.run([
        "ffmpeg", "-y", "-i", file_path, "-ar", "16000", "-ac", "1", output_path
    ], capture_output=True)
    return output_path

async def transcribe_and_send(file_path: str, send_message_threadsafe: callable):
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
        # os.remove(file_path) # clean up file after processing

async def flush_remaining_buffer(buffer: bytearray, webm_header: bytes, send_message_threadsafe: callable):
    if len(buffer) > 0:
        print(f"Flushing remaining buffer: {len(buffer)} bytes")
        audio_data = webm_header + bytes(buffer)
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        output_folder = os.path.join(BASE_DIR, "temp")
        file_path = os.path.join(output_folder, f"{uuid.uuid4()}.webm")
        with open(file_path, "wb") as f:
            f.write(audio_data)
        print(f"File written for remaining buffer: {file_path}")
        wav_path = convert_webm_to_wav(file_path)
        await transcribe_and_send(wav_path, send_message_threadsafe)
        buffer.clear() # clear buffer after flushing
        print("Finished flushing remaining buffer")
