# crawler.py
import feedparser
from newspaper import Article
from vectordb import save_to_vector_db  # Connects to your ChromaDB file

# NBC News public RSS endpoints (You can add more if you've broken them down into topics)
NBC_FEEDS = {
    "main": "https://feeds.nbcnews.com/nbcnews/public/news",
    "politics": "https://feeds.nbcnews.com/feeds/nbcpolitics",
    "business": "https://feeds.nbcnews.com/nbcnews/public/business"
}

def fetch_nbc_article_urls(feed_url):
    """Parses the NBC RSS feed to retrieve a clean list of article links."""
    print(f"Fetching RSS feed data from: {feed_url}")
    feed = feedparser.parse(feed_url)
    
    links = []
    for entry in feed.entries:
        # Check if a link exists in the feed entry
        if hasattr(entry, 'link'):
            links.append(entry.link)
            
    return list(set(links))  # De-duplicate links just in case

def process_and_store_article(url):
    """Downloads article body from NBC and updates your local Vector DB."""
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
        
        # Save to your local ChromaDB database file structure
        save_to_vector_db(article_data)
        return True
        
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return False

def run_nbc_crawler():
    print("=== STARTING NBC NEWS CRAWLER ===")
    
    # Grab the top stories feed
    target_feed = NBC_FEEDS["main"]
    article_links = fetch_nbc_article_urls(target_feed)
    
    print(f"Found {len(article_links)} recent articles in feed.")
    
    success_count = 0
    # Limit processing for testing (e.g., process the top 10 fresh articles)
    for link in article_links[:10]:
        print(f"Processing: {link}")
        if process_and_store_article(link):
            success_count += 1
            
    print(f"=== CRAWLER COMPLETE: Successfully saved {success_count} articles to ChromaDB ===")

if __name__ == "__main__":
    run_nbc_crawler()