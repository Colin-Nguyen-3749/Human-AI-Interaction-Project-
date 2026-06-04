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

        country TEXT,
        language TEXT,
        source_type TEXT,
        perspective_label TEXT,

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
            category,
            country,
            language,
            source_type,
            perspective_label
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article_data["title"],
            article_data["url"],
            article_data["publish_date"],
            article_data["source"],
            article_data["content"],
            article_data["summary"],
            article_data["category"],
            article_data["country"],
            article_data["language"],
            article_data["source_type"],
            article_data["perspective_label"],
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        print(f"Duplicate skipped: {article_data['url']}")

    finally:
        conn.close()