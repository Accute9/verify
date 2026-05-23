from fastapi import FastAPI
from .llm import generate_claim, separate_claim, evaluate_claim
from .search import retrieve_sources
import json
import asyncio

app = FastAPI()

@app.get("/")
def index():
    return {"message": "verify is working"}

@app.get("/fact-check")
async def fact_check():
    content = """“Nobody talks about this, but your phone is probably ruining your sleep even if you stop using it before bed. Researchers found that just having your phone in the same room can reduce sleep quality because your brain stays subconsciously alert. That’s why high performers leave their phones outside the bedroom completely. One study even showed people fell asleep faster and had deeper REM sleep after only three nights without a phone nearby.”"""
    evaluation = evaluate_claim(content)
    return evaluation

    
 
