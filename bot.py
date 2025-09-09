import requests
from bs4 import BeautifulSoup
import os
import json

URL = "https://www.pokemoncenter.com/category/new-releases"
KEYWORDS = ["TCG", "Elite Trainer Box", "Booster", "Collection"]

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")  # stored as a GitHub Secret

def fetch_products():
    response = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    items = []
    for product in soup.select("a[data-test='product-title']"):
        title = product.get_text(strip=True)
        link = "https://www.pokemoncenter.com" + product["href"]
        items.append({"title": title, "link": link})
    return items

def check_new():
    items = fetch_products()
    if os.path.exists("products.json"):
        with open("products.json", "r") as f:
            old_items = json.load(f)
    else:
        old_items = []

    old_titles = {item["title"] for item in old_items}
    new = [item for item in items if item["title"] not in old_titles]

    with open("products.json", "w") as f:
        json.dump(items, f)

    return [item for item in new if any(k in item["title"] for k in KEYWORDS)]

def notify_discord(item):
    if not DISCORD_WEBHOOK:
        print("⚠️ No Discord webhook set")
        return
    payload = {"content": f"🎉 New TCG Drop!\n{item['title']}\n{item['link']}"}
    requests.post(DISCORD_WEBHOOK, json=payload)

if __name__ == "__main__":
    new_items = check_new()
    if new_items:
        for item in new_items:
            print("NEW PRODUCT:", item["title"], item["link"])
            notify_discord(item)
