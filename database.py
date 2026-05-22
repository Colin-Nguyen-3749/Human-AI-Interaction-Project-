import sqlite3

database = "articles.db"

def connect_db():
    return sqlite3.connect(database)

def create_art_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS articles (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT,
                   url TEXT UNIQUE,
                   publish_date TEXT,
                   source TEXT,
                   content TEXT,
                   summary TEXT,
                   category TEXT,
                   scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                   )       
                   """)
    
    conn.commit()
    conn.close()

def article_exists(url):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id from articles WHERE url = ?",
        (url,)
    )

    result = cursor.fetchone()
    conn.close()
    return result is not None
    
def save_article(article_data):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO articles(
            title,
            url,
            publish_date,
            source,
            content,
            summary,
            category
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)               
        """, (
                article_data["title"],
                article_data["url"],
                article_data["publish_date"],
                article_data["source"],
                article_data["content"],
                article_data["summary"],
                article_data["category"],
            ))

        conn.commit()

    except sqlite3.IntegrityError:
        print(f"Duplicate skipL {article_data['url']}")
        
    conn.close()