def claim_evaluation_prompt(claim: str, subclaims: list, search_results: list) -> str:
    return f"""Given the claim {claim} , the subclaims {subclaims}, and the search results for these subclaims {search_results}:
    
    Evaluate each subclaim based on the search results, determining if the subclaim is supported, refuted, or inconclusive.

    Finally, use the evaluations of the subclaims to determine the overall veracity of the main claim, categorizing it as true, false, or mixed. 
    
    Return your evaluation in this raw JSON format with NO markdown: 
    {{"claim_evaluation": "true/false/mixed", 
    "confidence": average of subclaim confidence scores, 0.0-1.0, where a confidence score of 0.4 or below means evidence is weak/conflicting, and 1.0 means evidence is definitive",
    "subclaim_evaluations": [{{"subclaim": subclaim1, "evaluation": "supported/refuted/inconclusive", "subclaim_confidence_score": score 0.0-1.0, (a confidence score of 0.4 or below mean evidence is weak/conflicting, 1.0 means evidence is definitive)}}, ...],
    "reasoning": "2-3 sentences explaining verdict, referencing specific sources",
    "key_source": "url of the most important source that influenced your evaluation"
    }}.
    
    Each evaluation should be no longer than a sentence, and should be based solely on the information provided in the search results. Do not use any outside knowledge or assumptions.
    
    Raw JSON only, no markdown.
    
    """