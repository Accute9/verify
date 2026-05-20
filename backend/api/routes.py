from fastapi import FastAPI
from .llm import generate_claim
from .prompts.claim_prompt import claim_prompt

app = FastAPI()

@app.get("/")
def index():
    return {"message": "verify is working"}

@app.get("/fact-check")
async def fact_check():
    content = """“Nobody talks about this, but your phone is probably ruining your sleep even if you stop using it before bed. Researchers found that just having your phone in the same room can reduce sleep quality because your brain stays subconsciously alert. That’s why high performers leave their phones outside the bedroom completely. One study even showed people fell asleep faster and had deeper REM sleep after only three nights without a phone nearby.”"""
    # print(generate_claim("The Eiffel Tower is located in Paris, France. It was completed in 1889 and is one of the most recognizable landmarks in the world."))
    return {"claim": generate_claim(claim_prompt.format(content=content))}
 