def claim_search_prompt(subclaim: str) -> str:
    return f"""Subclaim: {subclaim}. Find relevant evidence sources for each subclaim.
    Format:
    [
    claim1: [
        {{
        "title": "...",
        "url": "...",
        "summary": "...", (1 sentence)
        "cred_score": 8 (1-10)
        }}
    ],
    claim2: [...]
    ]
    """