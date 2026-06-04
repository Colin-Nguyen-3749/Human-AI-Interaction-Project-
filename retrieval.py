import sqlite3

DATABASE = "articles.db"

def search_articles(query, limit=5):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    wildcard_query = f"%{query}%"

    cursor.execute("""
        SELECT
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
        FROM articles
        WHERE
            title LIKE ?
            OR content LIKE ?
            OR summary LIKE ?
        ORDER BY scraped_at DESC
        LIMIT ?
    """, (
        wildcard_query,
        wildcard_query,
        wildcard_query,
        limit
    ))

    rows = cursor.fetchall()
    conn.close()

    articles = []

    for row in rows:
        articles.append({
            "title": row["title"],
            "url": row["url"],
            "publish_date": row["publish_date"],
            "source": row["source"],
            "content": row["content"],
            "summary": row["summary"],
            "category": row["category"],
            "country": row["country"],
            "language": row["language"],
            "source_type": row["source_type"],
            "perspective_label": row["perspective_label"]
        })

    return articles