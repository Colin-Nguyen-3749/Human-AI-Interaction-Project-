import os
import requests

from webCrawl import crawl_urls_from_search_results

NEWS_API_KEY = os.getenv("NEWS_API_KEY")


def search_news_api(query, limit=5):
    if not NEWS_API_KEY:
        print("Missing NEWS_API_KEY")
        return []

    url = "https://newsapi.org/v2/everything"

    params = {
        "apiKey": NEWS_API_KEY,
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": limit,
    }

    response = requests.get(url, params=params, timeout=15)

    if response.status_code != 200:
        print("NewsAPI error:", response.status_code, response.text)
        return []

    data = response.json()

    urls = []

    for article in data.get("articles", []):
        article_url = article.get("url")
        if article_url:
            urls.append(article_url)

    return urls


def dynamic_ingest_from_user_query(user_query, limit=5):

    deeper_words = ["deeper", "in-depth", "comprehensive", "more","explain","context","background","why"]
    if any(word in user_query.lower() for word in deeper_words):
        # logic to provide deeper context or background information
        search_query = f"{user_query} analysis background context"

    else:
        search_query = user_query

    urls = search_news_api(search_query, limit=limit)

    if not urls:
        return 0

    saved_count = crawl_urls_from_search_results(
        article_urls=urls,
        source_name="NewsAPI Live Search",
        source_meta={
            "country": "Mixed",
            "language": "en",
            "source_type": "live search",
            "perspective_label": "live web result",
        }
    )

    return saved_count