def claim_evaluation_prompt(claim: str, subclaims: list, search_results: list) -> str:
    return f"""Given the claim {claim} , the subclaims {subclaims}, and the search results for these subclaims {search_results}:
    
    Evaluate each subclaim based on the search results, determining if the subclaim is supported, refuted, or inconclusive.

    Finally, use the evaluations of the subclaims to determine the overall veracity of the main claim, categorizing it as true, false, or mixed. 
    
    Return your evaluation in this raw JSON format with NO markdown: 
    {{
    "claim_evaluation": "true/false/mixed",
    "confidence": 0.0,
    "subclaim_evaluations": [
        {{
        "subclaim": "subclaim1",
        "evaluation": "supported/refuted/inconclusive",
        "subclaim_confidence_score": 0.0
        }}
    ],
    "reasoning": "1-2 sentences explaining the verdict, referencing specific sources. No more than 30 words total.",
    "key_source": "https://example.com"
    }}
    
    Each evaluation should be no longer than a sentence, and should be based ONLY off of info from search results. DO NOT use any outside information or assumptions.
    Raw JSON only, no markdown.
    
    """