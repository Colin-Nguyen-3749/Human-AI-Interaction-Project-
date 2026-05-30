# crawler.py
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
    },

    "Reuters": {
        "main": "https://feeds.reuters.com/reuters/topNews"
    },

    "BBC": {
        "main": "http://feeds.bbci.co.uk/news/rss.xml"
    },
    #forbes not working?
    #"Forbes" : {
       # "main": "https://www.forbes.com/business/feed/"
   # },

    "NBC Politics" :{
        "main" : "https://feeds.nbcnews.com/feeds/nbcpolitics"
    },

    "NBC Business" : {
        "main" : "https://feeds.nbcnews.com/nbcnews/public/business"
    },

   "Conversation Feed" : {
       "main" : "theconversation.com/us/articles"
   },

   "Alternet Feed" : {
       "main" : "alternet.org/feeds/feed.rss"
   }
}
#switch from testing nbc to all the urls fed to it
def fetch_nbc_article_urls(feed_url):
    """Parses to retrieve a clean list of article links."""
    print(f"Fetching RSS feed data from: {feed_url}")
    feed = feedparser.parse(feed_url)
    
    links = []
    for entry in feed.entries:
        # Check if a link exists in the feed entry
        if hasattr(entry, 'link'):
            links.append(entry.link)
            
    return list(set(links))  # De-duplicate links just in case

def process_and_store_article(url, source_name):
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
            
        article_data = {
            "title": article.title,
            "text": article.text,
            "publish_date": article.publish_date if article.publish_date else "Unknown",
            "url": url
        }
        save_article({
            "title": article.title,
            "url": url,
            "publish_date": str(article.publish_date),
            "source": source_name,
            "content": article.text,
            "summary": article.text[:300],
            "category": "news"
        })

        # Save to local ChromaDB database
        save_to_vector_db(article_data)
        return True
        
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return False

#implement user input and then fetch articles/crawl articles based on it (RAG Chatbot automation)
#use cos. vector for similarilty

#issue: limit of article already exists??

def run_nbc_crawler():
    print("=== STARTING NBC NEWS CRAWLER ===")
    
    create_art_tables()

    success_count = 0

    # Grab the top stories feed
    for source_name, feeds in NEWS_FEEDS.items():
        target_feed = feeds["main"]
        print(f"\n=== FETCHING FROM {source_name} ===")
        article_links = fetch_nbc_article_urls(target_feed)
        print(f"Found {len(article_links)} recent articles in feed.")
    
    # Limit processing for testing (e.g., process the top 10 fresh articles)
        for link in article_links[:10]:
            print(f"Processing: {link}")
            if process_and_store_article(link, source_name):
                success_count += 1
            
    print(f"=== CRAWLER COMPLETE: Successfully saved {success_count} articles to ChromaDB ===")

if __name__ == "__main__":
    run_nbc_crawler() 