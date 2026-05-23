from fastapi import APIRouter
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
import httpx
import json
import asyncio
from .prompts.claim_generation_prompt import claim_generation_prompt
from .prompts.claim_separator_prompt import claim_separator_prompt
from .prompts.claim_evaluation_prompt import claim_evaluation_prompt
from .search import retrieve_sources
# from .prompts.claim_search_prompt  import claim_search_prompt

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
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
    )
    return (request.json())["choices"][0]["message"]["content"]

def generate_claim(content: str):
    user = claim_generation_prompt(content)
    return call_llm(SYSTEM_PROMPT, user)

def separate_claim(claim: str):
    user = claim_separator_prompt(claim)
    return call_llm(SYSTEM_PROMPT, user)

def average_confidence(evaluation_data: str) -> float:
    scores = [subclaim["subclaim_confidence_score"] for subclaim in evaluation_data["subclaim_evaluations"]]
    return sum(scores) / len(scores) if scores else 0.0

def evaluate_claim(content: str):
    generated_claim = json.loads(generate_claim(content))["claim"]
    subclaims = json.loads(separate_claim(generated_claim))["subclaims"]
    search_results = [retrieve_sources(cl) for cl in subclaims]
    user = claim_evaluation_prompt(generated_claim, subclaims, search_results)
    eval_data = call_llm(SYSTEM_PROMPT, user)
    avg_confidence = average_confidence(json.loads(eval_data))
    return {
        "claim_evaluation": json.loads(eval_data)["claim_evaluation"],
        "confidence": avg_confidence,
        "subclaim_evaluations": json.loads(eval_data)["subclaim_evaluations"],
        "reasoning": json.loads(eval_data)["reasoning"],
        "key_source": json.loads(eval_data)["key_source"]
    }
    # return eval_data
    
print(evaluate_claim("""Nobody talks about this, but your phone is probably ruining your sleep even if you stop using it before bed. Researchers found that just having your phone in the same room can reduce sleep quality because your brain stays subconsciously alert. That’s why high performers leave their phones outside the bedroom completely. One study even showed people fell asleep faster and had deeper REM sleep after only three nights without a phone nearby."""))