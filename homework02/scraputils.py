import re

import requests
from bs4 import BeautifulSoup

HABR_URL = "https://habr.com"


def _text(tag):
    return tag.get_text(strip=True) if tag else ""


def extract_news(parser):
    """ Extract news from a given web page """
    news_list = []

    for article in parser.find_all("article"):
        link = article.select_one("h2 a[href]")
        if link is None:
            continue

        url = link["href"]
        if url.startswith("/"):
            url = HABR_URL + url

        # идентификатор статьи: атрибут id карточки, а если его нет, то число из ссылки
        habr_id = article.get("id")
        if not habr_id:
            match = re.search(r"/(\d+)/?", link["href"])
            habr_id = match.group(1) if match else None

        author = article.select_one("a.tm-user-info__username") or article.select_one('a[href*="/users/"]')
        complexity = article.select_one(".tm-article-complexity__label") or article.select_one(
            '[class*="complexity__label"]'
        )

        news_list.append(
            {
                "title": _text(link),
                "author": _text(author),
                "url": url,
                "complexity": _text(complexity),
                "habr_id": habr_id,
            }
        )

    return news_list


def extract_next_page(parser):
    """ Extract next page URL """
    link = parser.select_one("a#pagination-next-page") or parser.select_one("a[rel~=next]")
    return link["href"] if link is not None and link.has_attr("href") else None


def get_news(url, n_pages=1):
    """ Collect news from a given web page """
    news = []
    while n_pages:
        print("Collecting data from page: {}".format(url))
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = extract_news(soup)
        next_page = extract_next_page(soup)
        news.extend(news_list)
        n_pages -= 1
        if not next_page:
            break
        url = HABR_URL + next_page
    return news
