from fastapi import APIRouter
# from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from .prompts.claim_generation_prompt import claim_generation_prompt
from .prompts.claim_separator_prompt import claim_separator_prompt
from langchain_openrouter import ChatOpenRouter
import httpx

router = APIRouter()
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SYSTEM_PROMPT = "You are a fact-checking assistant. Output only valid JSON"

def call_llm(system: str, user: str) -> str:
    request = httpx.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        },
        json={
            "model": "google/gemini-2.5-flash",
            "max_tokens": 1000,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
    )
    return (request.json())["choices"][0]["message"]["content"]

def generate_claim(content: str):
    system = SYSTEM_PROMPT
    user = claim_generation_prompt(content)
    return call_llm(system, user)

def separate_claim(claim: str):
    system = SYSTEM_PROMPT
    user = claim_separator_prompt(claim)
    return call_llm(system, user)

# print(generate_claim(claim_prompt.format(content="The Eiffel Tower is located in Paris, France. It was completed in 1889 and is one of the most recognizable landmarks in the world.")))
# print(separate_claim(claim_separator_prompt.format(claim="Vitamin C cures the flu in 24 hours")))
