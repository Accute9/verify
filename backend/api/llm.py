from fastapi import APIRouter
# from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from .prompts.claim_prompt import claim_prompt
from langchain_openrouter import ChatOpenRouter
import httpx

router = APIRouter()
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_claim(prompt: str) -> str:
    """
    What I need to do: send a request to the openrouter API with the claim prompt and return the generated claim
    """
    request = httpx.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}"
        },
        json={
            "model":"google/gemini-2.5-flash",
            "max_tokens":1000,
            "messages":[
                {"role":"user","content": prompt}
            ],
        }
    )
    return (request.json())["choices"][0]["message"]["content"]

# print(generate_claim(claim_prompt.format(content="The Eiffel Tower is located in Paris, France. It was completed in 1889 and is one of the most recognizable landmarks in the world.")))
