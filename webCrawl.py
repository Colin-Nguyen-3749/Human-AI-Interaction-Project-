# crawler.py

import time
from typing import Dict, List

import feedparser
from newspaper import Article

from vectordb import save_to_vector_db  # Connects to your ChromaDB file
from database import (
    create_art_tables,
    save_article,
    article_exists
)

#news to build database and their RSS feed urls
NEWS_FEEDS = {
    "NBC Main News": {
        "main": "https://feeds.nbcnews.com/nbcnews/public/news",
        "country": "United States",
        "language": "en",
        "source_type": "corporate media",
        "perspective_label": "US mainstream",
    },

    "BBC": {
        "main": "http://feeds.bbci.co.uk/news/rss.xml",
        "country": "United Kingdom",
        "language": "en",
        "source_type": "public broadcaster",
        "perspective_label": "UK/global public broadcaster",
    },

    "NBC Politics" :{
        "main" : "https://feeds.nbcnews.com/feeds/nbcpolitics",
        "country": "United States",
        "language": "en",
        "source_type": "corporate media",
        "perspective_label": "US mainstream",
    },

    "NBC Business" : {
        "main" : "https://feeds.nbcnews.com/nbcnews/public/business",
        "country": "United States",
        "language": "en",
        "source_type": "corporate media",
        "perspective_label": "US mainstream",
    },

   "Conversation Feed" : {
       "main" : "https://theconversation.com/us/articles.atom",
       "country": "United States",
       "language": "en",
       "source_type": "academic commentary",
       "perspective_label": "expert/academic analysis",
   },

   "Alternet Feed" : {
       "main" : "https://alternet.org/feeds/feed.rss",
       "country": "United States",
       "language": "en",
       "source_type": "independent media",
       "perspective_label": "US progressive",
   },

   "Al Jazeera" : {
       "main" : "https://www.aljazeera.com/xml/rss/all.xml",
       "country": "Qatar",
       "language": "en",
       "source_type": "international media",
       "perspective_label": "non-Western global outlet",
   },

    "CNBC Business": {
    "main": "https://www.cnbc.com/id/10001147/device/rss/rss.html",
    "country": "United States",
    "language": "en",
    "source_type": "business media",
    "perspective_label": "US business/markets",
},

"BBC Business": {
    "main": "https://feeds.bbci.co.uk/news/business/rss.xml",
    "country": "United Kingdom",
    "language": "en",
    "source_type": "public broadcaster",
    "perspective_label": "UK/global business",
},

"BBC Technology": {
    "main": "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "country": "United Kingdom",
    "language": "en",
    "source_type": "public broadcaster",
    "perspective_label": "UK/global technology",
},

"BBC Entertainment": {
    "main": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml",
    "country": "United Kingdom",
    "language": "en",
    "source_type": "public broadcaster",
    "perspective_label": "UK/global entertainment",
},

"ESPN": {
    "main": "https://www.espn.com/espn/rss/news",
    "country": "United States",
    "language": "en",
    "source_type": "sports media",
    "perspective_label": "US sports",
},

"Variety": {
    "main": "https://variety.com/feed/",
    "country": "United States",
    "language": "en",
    "source_type": "entertainment media",
    "perspective_label": "US entertainment industry",
},

"NPR": {
    "main": "https://feeds.npr.org/1001/rss.xml",
    "country": "United States",
    "language": "en",
    "source_type": "public/nonprofit media",
    "perspective_label": "US public radio",
},

"AP News": {
    "main": "https://apnews.com/hub/ap-top-news?output=rss",
    "country": "United States",
    "language": "en",
    "source_type": "wire service",
    "perspective_label": "US/global wire service",
},
   
}

#switch from testing nbc to all the urls fed to it
def fetch_article_urls(feed_url) -> List[str]:
    """Parses to retrieve a clean list of article links."""
    print(f"Fetching RSS feed data from: {feed_url}")
    feed = feedparser.parse(feed_url)
    
    links = []
    for entry in feed.entries:
        # Check if a link exists in the feed entry
        link = getattr(entry, "link", None)
        if link:
            links.append(link)
            
    return list(dict.fromkeys(links))  # De-duplicate links just in case

def process_and_store_article(url, source_name, source_meta):
    """Downloads article body from NBC, update vector database"""

    if article_exists(url):
        print("Article already exists.")
        return False
    
    try:
        article = Article(url)
        article.download()
        article.parse()
        
        # Verify text was actually extracted (skips video-only pages)
        if not article.text or len(article.text.strip()) < 100:
            return False
            
        publish_date = article.publish_date if article.publish_date else "Unknown"
        summary = article.text[:500]  # Simple summary: first 500 chars
        
        article_data = {
            "title": article.title or "Untitled",
            "url": url,
            "publish_date": str(publish_date),
            "source": source_name,
            "content": article.text,
            "text": article.text,
            "summary": summary,
            "category": "news",
            "country": source_meta.get("country", "Unknown"),
            "language": source_meta.get("language", "en"),
            "source_type": source_meta.get("source_type", "news"),
            "perspective_label": source_meta.get("perspective_label", "unspecified"),
        }
        sql_saved = save_article(article_data)
        vector_saved = save_to_vector_db(article_data)

        return sql_saved and vector_saved

    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return False

#implement user input and then fetch articles/crawl articles based on it (RAG Chatbot automation)
#use cos. vector for similarilty

#issue: limit of article already exists??

def run_news_crawler():
    print("=== STARTING NEWS CRAWLER ===")

    create_art_tables()

    success_count = 0

    # Grab the top stories feed
    for source_name, feeds in NEWS_FEEDS.items():
        target_feed = feeds["main"]
        print(f"\n=== FETCHING FROM {source_name} ===")
        article_links = fetch_article_urls(target_feed)
        print(f"Found {len(article_links)} recent articles in feed.")
    
    # Limit processing for testing (e.g., process the top 10 fresh articles)
        for link in article_links[:100]:
            print(f"Processing: {link}")
            if process_and_store_article(link, source_name, feeds):
                success_count += 1
            time.sleep(1)
            
    print(f"=== CRAWLER COMPLETE: Successfully saved {success_count} articles to ChromaDB ===")

def crawl_urls_from_search_results(article_urls, source_name="Live Search", source_meta=None):
    if source_meta is None:
        source_meta = {
            "country": "Unknown",
            "language": "en",
            "source_type": "live search",
            "perspective_label": "search result",
        }

    saved_count = 0

    for url in article_urls:
        print(f"Live crawling: {url}")

        if process_and_store_article(url, source_name, source_meta):
            saved_count += 1

        time.sleep(1)

    return saved_count

if __name__ == "__main__":
    run_news_crawler()