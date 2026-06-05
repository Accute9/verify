import whisper
import asyncio
import json

model = whisper.load_model("tiny")

def transcribe_audio(file_path: str) -> str:
    result = model.transcribe(file_path)
    return result["text"]

