from bs4 import BeautifulSoup
import httpx
import supabase

def scrape_politifact(pages: int = 10):
    for page in range(1, pages + 1):
        URL = f"https://www.politifact.com/factchecks/list/?page={page}"
        response = httpx.get(URL.format(page), headers={
            "User-Agent": "Mozilla/5.0"
        })
        soup = BeautifulSoup(response.text, "html.parser")
        for item in soup.select(".m-statement__quote"):
            claim = item.get_text(strip=True)
            print("CLAIM: " +  claim)
            eval = item.find_next("div", class_="m-statement__meter").get_text(strip=True) if item.find_next("div", class_="m-statement__meter")
            summary_el = soup.find("meta", id="description")
            summary = summary_el.get("content") if summary_el else None
            

