import requests
import re
import json
from bs4 import BeautifulSoup


def scrape_page(
    base_url: str, image_selector: str, title_selector: str, description_selector: str
):
    response = requests.get(base_url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    script_tag = soup.find("script", type="application/ld+json")

    # images = soup.select(image_selector)
    # title = soup.select(title_selector)
    # description = soup.select(description_selector)

    # return {
    #     "images": [el.get("src") for el in images if el.get("src")],
    #     "title": title[0].get_text(strip=True),
    #     "description": description[0].get_text(strip=True),
    # }
    if script_tag:
        json_data = json.loads(script_tag.string)

        return {
            "images": json_data.get(image_selector, ""),
            "title": json_data.get(title_selector, ""),
            "description": json_data.get(description_selector, ""),
        }


def scrape_listing_page(
    base_url: str, image_selector: str, title_selector: str, description_selector: str
):
    resp = requests.get(base_url)
    soup = BeautifulSoup(resp.text, "html.parser")

    listing_items = []
    for header in soup.select("h2, h3"):
        text = header.get_text(strip=True)
        if text:
            link = header.find_next("a")
            href = link["href"] if link and link.has_attr("href") else None
            listing_items.append({"title": text, "url": href})

    scraped_data = []
    if len(listing_items) > 0:
        for element in listing_items[:10]:
            try:
                scraped_data.append(
                    scrape_page(
                        base_url=element.get("url"),
                        image_selector=image_selector,
                        title_selector=title_selector,
                        description_selector=description_selector,
                    )
                )
            except Exception as e:
                pass
    return scraped_data
