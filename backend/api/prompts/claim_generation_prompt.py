def claim_generation_prompt(content: str) -> str:
    return f"""Compose a single claim from the following text. The claim should be concise and capture the main point of the text, and can be multiple parts if needed: {content}.

    Return your answer in this raw JSON format with NO markdown:
    {{"claim": "the composed claim"}}

    Raw JSON only, no markdown."""