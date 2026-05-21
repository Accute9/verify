def claim_separator_prompt(claim: str) -> str:
    return f"""Given the claim {claim}, separate the claim into easily searchable pieces that can be separately verified. 
    
    Return these components in this JSON format: {{"subclaims": [subclaim1, subclaim2, subclaim3...]}}."""

