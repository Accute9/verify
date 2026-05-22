import httpx
from dotenv import load_dotenv
import os
from prompts.claim_search_prompt  import claim_search_prompt
from tavily import TavilyClient
import json

load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
# print(SERPER_API_KEY)

# def retrieve_sources(subclaim: str):
#     search_prompt = claim_search_prompt(subclaim)
#     querystring = {"query": search_prompt, "count":"3","language":"EN","crawl_timeout":"10"}

#     headers = {
#         "X-Subscription-Token": SEARCH_API_KEY,
#         "Accept": "application/json"
#     }
#     response = httpx.get(url, headers=headers, params=querystring)

#     return response.json()

def retrieve_sources(subclaim: str):
    # search_prompt = claim_search_prompt(subclaim)
    search_prompt = subclaim
    response = httpx.post(
        "https://google.serper.dev/search",
        headers={
            "X-API-KEY": os.environ["SERPER_API_KEY"],
            "Content-Type": "application/json"
        },
        json={
            "q": search_prompt,
            "num": 3
        }
    ).json()
    q = response["searchParameters"]["q"]
    clean_results = [
        {
            "query": q,
            "title": result["title"],
            "url": result["link"],
        } for result in response.get("organic", [])
    ]
    return clean_results




print(retrieve_sources("Having a phone in the bedroom can lead to reduced sleep quality"))
    