from bs4 import BeautifulSoup
import httpx
import re
from backend.api.database.load_db import supabase, generate_bigint_id

def normalize_politifact_verdict(verdict: str) -> str:
    mapping = {
        "true": "true",
        "mostly-true": "true",
        "half-true": "mixed",
        "barely-true": "mixed",
        "false": "false",
        "pants-fire": "false"
    }
    return mapping.get(verdict.lower().replace(" ", "-"), "mixed")

def store_scrapped_eval_data(eval_id: int, claim: str, verdict_text: str, author: str, date: str):
        supabase.table("ece_calibration").insert({
        "eval_id": eval_id,
        "claim": claim,
        "eval": normalize_politifact_verdict(verdict_text),
        "author": author,
        "date": date,
        "source": "politifact"
    }).execute()

def scrape_politifact(pages: int = 1):
    for page in range(2, pages + 1):
        URL = f"https://www.politifact.com/factchecks/list/?page={page}"
        response = httpx.get(URL.format(page), headers={
            "User-Agent": "Mozilla/5.0"
        })
        soup = BeautifulSoup(response.text, "html.parser")
        for item in soup.select(".m-statement"):
            claim = item.select_one(".m-statement__quote a")
            claim_text = claim.get_text(strip=True) if claim else "No claim found"
            speaker = item.select_one(".m-statement__name")
            speaker_text = speaker.get_text(strip=True) if speaker else "No speaker found"
            verdict = item.select_one(".m-statement__meter img")
            verdict_text = verdict.get("alt") if verdict else "No verdict found"
            footer = item.select_one(".m-statement__footer")
            footer_text = footer.get_text(strip=True) if footer else "No footer found"
            author, date = None, None
            match = re.search(r"By (.+?)\s*•\s*(.+)", footer_text)
            if match:
                author = match.group(1).strip()
                date = match.group(2).strip()

            if claim_text and verdict:
                store_scrapped_eval_data(eval_id=generate_bigint_id(), claim=claim_text, verdict_text=verdict_text, author=speaker_text, date=date)
            # print("CLAIM: " + claim_text)
            # eval = item.find_next("div", class_="m-statement__meter").get_text(strip=True) if item.find_next("div", class_="m-statement__meter") else "No evaluation found"
            # summary_el = soup.find("meta", id="description")
            # summary = summary_el.get("content") if summary_el else None

            # print("EVAL: " + eval)
            # print("SUMMARY: " + summary)
            # store_scrapped_eval_data(eval_id=generate_bigint_id(), claim=claim_text, eval=eval, source="Politifact", summary=summary)


if __name__ == "__main__":
    scrape_politifact(pages=10)