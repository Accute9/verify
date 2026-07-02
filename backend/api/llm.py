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

async def call_llm(system: str, user: str, retries: int = 3) -> str:
    for attempt in range(retries):
        async with httpx.AsyncClient(timeout=60.0) as client:
            request = await client.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                },
                json={
                    "model": "google/gemini-2.5-flash",
                    "max_tokens": 2500,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                },
            )
        # return parse_llm_response((request.json())["choices"][0]["message"]["content"])
        resp = request.json()
        # print(resp)  # see the actual error
        content = parse_llm_response(resp["choices"][0]["message"]["content"])
        try:
            json.loads(content)  # Validate JSON
            return content
        except json.JSONDecodeError:
            if attempt == retries - 1:
                raise print(f"Failed to parse JSON after {retries} attempts. Last response: {content}")

def parse_llm_response(response: str) -> str:
    return (
        response.strip()
        .replace("\n", "")
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

async def generate_claim(content: str):
    user = claim_generation_prompt(content)
    raw = await call_llm(SYSTEM_PROMPT, user)
    print(raw)
    return raw

async def separate_claim(claim: str):
    user = claim_separator_prompt(claim)
    raw =  await call_llm(SYSTEM_PROMPT, user)
    print(raw)
    return raw

def average_confidence(evaluation_data: str) -> float:
    scores = [subclaim["subclaim_confidence_score"] for subclaim in evaluation_data["subclaim_evaluations"]]
    return sum(scores) / len(scores) if scores else 0.0

async def evaluate_claim(content: str, transcript_id: int = None, eval_id: int = None) -> dict:
    generated_claim = json.loads(await generate_claim(content))["claim"]
    subclaims = json.loads(await separate_claim(generated_claim))["subclaims"]
    start = time.perf_counter()
    async with httpx.AsyncClient(timeout=20.0) as client:
        search_results = await asyncio.gather(*[retrieve_sources(cl, client) for cl in subclaims])
    latency = time.perf_counter() - start
    print(f"Search latency: {latency:.2f} seconds")

    user = claim_evaluation_prompt(generated_claim, subclaims, search_results)
    eval_data = json.loads(await call_llm(SYSTEM_PROMPT, user))
    avg_confidence = average_confidence(eval_data)

    claim_id = generate_bigint_id()
    store_claim_evaluation(claim_id, eval_data["claim_evaluation"], avg_confidence, eval_data["reasoning"], transcript_id=transcript_id, eval_id=eval_id)
    store_subclaim_evaluations(eval_data["subclaim_evaluations"], claim_id, search_results)

    return_dict = {
        "claim_evaluation": eval_data["claim_evaluation"],
        "confidence": avg_confidence,
        "subclaim_evaluations": eval_data["subclaim_evaluations"],
        "reasoning": eval_data["reasoning"],
        "key_source": eval_data["key_source"]
    }

    return return_dict

# if __name__ == "__main__":
#     # evaluated_claim = asyncio.run(evaluate_claim("The Earth is flat.", 12345))
#     eval = asyncio.run(evaluate_claim("The Earth is flat.", eval_id=2887746228259398511))
#     print(eval)