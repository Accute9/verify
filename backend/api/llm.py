from fastapi import APIRouter
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
import httpx
import json
import asyncio
import time
from .prompts.claim_generation_prompt import claim_generation_prompt
from .prompts.claim_separator_prompt import claim_separator_prompt
from .prompts.claim_evaluation_prompt import claim_evaluation_prompt
from .search import retrieve_sources
from .database.load_db import store_subclaim_evaluations, store_claim_evaluation, generate_bigint_id

# from .prompts.claim_search_prompt  import claim_search_prompt

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SYSTEM_PROMPT = "You are a fact-checking assistant. Output only valid JSON"

async def call_llm(system: str, user: str) -> str:
    async with httpx.AsyncClient(timeout=60.0) as client:
        request = await client.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            },
            json={
                "model": "google/gemini-2.5-flash",
                "max_tokens": 3500,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            },
        )
        body = request.json()
        if "choices" not in body:
            raise RuntimeError(f"OpenRouter request failed: {body}")
        choice = body["choices"][0]
        if choice.get("finish_reason") == "length":
             raise RuntimeError(
                "LLM response was truncated (hit max_tokens) before finishing JSON output." 
            )
        return parse_llm_response(choice["message"]["content"])

def parse_llm_response(response: str) -> str:
    return (
        response.strip()
        .replace("\n", "")
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

async def call_llm_json(system: str, user: str, retries: int = 1) -> dict:
    last_response = None
    for attempt in range(retries + 1):
        last_response = await call_llm(system, user)
        try:
            return json.loads(last_response)
        except json.JSONDecodeError:
            if attempt == retries:
                print(f"Failed to parse LLM response as JSON:\n{last_response}")
                raise

async def generate_claim(content: str) -> dict:
    user = claim_generation_prompt(content)
    return await call_llm_json(SYSTEM_PROMPT, user)

async def separate_claim(claim: str) -> dict:
    user = claim_separator_prompt(claim)
    return await call_llm_json(SYSTEM_PROMPT, user)

def average_confidence(evaluation_data: str) -> float:
    scores = [subclaim["subclaim_confidence_score"] for subclaim in evaluation_data["subclaim_evaluations"]]
    return sum(scores) / len(scores) if scores else 0.0

async def evaluate_claim(content: str, transcript_id: int) -> dict:
    generated_claim = (await generate_claim(content))["claim"]
    subclaims = (await separate_claim(generated_claim))["subclaims"]
    start = time.perf_counter()
    async with httpx.AsyncClient(timeout=20.0) as client:
        search_results = await asyncio.gather(*[retrieve_sources(cl, client) for cl in subclaims])
    latency = time.perf_counter() - start
    print(f"Search latency: {latency:.2f} seconds")

    user = claim_evaluation_prompt(generated_claim, subclaims, search_results)
    eval_data = await call_llm_json(SYSTEM_PROMPT, user)
    avg_confidence = average_confidence(eval_data)

    claim_id = generate_bigint_id()
    # store_claim_evaluation(claim_id, transcript_id, eval_data["claim_evaluation"], avg_confidence, eval_data["reasoning"])
    # store_subclaim_evaluations(eval_data["subclaim_evaluations"], claim_id, search_results)

    return_dict = {
        "claim_evaluation": eval_data["claim_evaluation"],
        "confidence": avg_confidence,
        "subclaim_evaluations": eval_data["subclaim_evaluations"],
        "reasoning": eval_data["reasoning"],
        "key_source": eval_data["key_source"]
    }

    return return_dict

