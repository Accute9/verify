import httpx
from dotenv import load_dotenv
import os
from .prompts.claim_search_prompt  import claim_search_prompt
from tavily import TavilyClient

load_dotenv()
SEARCH_API_KEY = os.getenv("SEARCH_API_KEY")
print(SEARCH_API_KEY)

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
    client = TavilyClient(SEARCH_API_KEY)
    search_prompt = claim_search_prompt(subclaim)
    response = client.search(search_prompt, num_results=3)
    return response




print(retrieve_sources("Having a phone in the same room can reduce sleep quality, even if not actively used, due to subconscious alertness."))
