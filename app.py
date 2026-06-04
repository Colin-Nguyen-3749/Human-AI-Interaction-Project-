# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

from database import connect_db, create_art_tables
from retrieval import search_articles
from vectordb import query_knowledge_base

from live_search import dynamic_ingest_from_user_query

app = Flask(__name__)
CORS(app)  # Allows your frontend script.js to communicate with this backend

CLOUDFLARE_WORKER_URL = "https://reroot-the-third.nguyen-c9.workers.dev/"

create_art_tables()

def get_recent_articles(limit=10):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            title,
            url,
            source,
            publish_date,
            content,
            summary,
            category,
            country,
            language,
            source_type,
            perspective_label
        FROM articles
        ORDER BY scraped_at DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    articles = []

    for row in rows:
        articles.append({
            "title": row[0],
            "url": row[1],
            "source": row[2],
            "publish_date": row[3],
            "content": row[4],
            "summary": row[5],
            "category": row[6],
            "country": row[7],
            "language": row[8],
            "source_type": row[9],
            "perspective_label": row[10],
        })

    return articles

@app.route("/api/articles", methods=["GET"])
def fetch_articles():
    articles = get_recent_articles(limit=10)
    return jsonify(articles)

@app.route("/api/chat", methods=["POST"])
def chat_bridge():
    try:
        data = request.json
        if isinstance(data, list):
            conversation_history = data

        elif isinstance(data, dict):
            conversation_history = data.get("messages", [])

        else:
            conversation_history = []

        if not conversation_history:
            return jsonify({"message": "Invalid history"}), 400

        # 1. Grab the very last message the user typed
        user_message_obj = conversation_history[-1]
        user_query = user_message_obj["content"]

        # 2. Query your local articles matching that query
        recent_keywords = [
            "latest",
            "recent",
            "today",
            "newest",
            "breaking",
            "headlines",
            "current news"
        ]

        is_recent_request = any(
            keyword in user_query.lower()
            for keyword in recent_keywords
        )

        recent_request_instruction = ""

        if is_recent_request:
            relevant_articles = get_recent_articles(limit=5)
            
            recent_request_instruction = """
            This is a general recent-news request.
            Give only 3-5 diverse stories.
            Do not overfocus on one region or topic.
            After summarizing, ask which topic the user wants next:
            world, US, technology, finance, sports, entertainment, health/science, or culture.
            """

        else:
            # Step 1: search ChromaDB
            relevant_articles = query_knowledge_base(user_query, limit=5)
            
            # Detect whether retrieved articles actually match the user's topic
            query_words = user_query.lower().split()

            matching_articles = []

            for article in relevant_articles:
                combined_text = (
                    str(article.get("title", "")) + " " +
                    str(article.get("content", "")) + " " +
                    str(article.get("text", ""))
                ).lower()

                if any(word in combined_text for word in query_words):
                    matching_articles.append(article)

                # Replace with only relevant matches
                relevant_articles = matching_articles

            # Step 2: search SQLite fallback
            if not relevant_articles:
                relevant_articles = search_articles(user_query, limit=5)

            # Step 3: if not enough results, search live web and save new articles
            if not relevant_articles or len(relevant_articles) < 2:
                saved_count = dynamic_ingest_from_user_query(user_query, limit=5)
                print(f"Dynamically saved {saved_count} new articles.")

                # Step 4: search again after saving
                relevant_articles = query_knowledge_base(user_query, limit=5)

                if not relevant_articles:
                    relevant_articles = search_articles(user_query, limit=5)

        # 3. Format the news findings into a clear text snippet
        context = ""

        clean_articles = []

        if relevant_articles:
            for item in relevant_articles:
                if isinstance(item, list):
                    for subitem in item:
                        if isinstance(subitem, dict):
                            clean_articles.append(subitem)
                elif isinstance(item, dict):
                    clean_articles.append(item)

        if clean_articles:
            context = "\n\n[RELEVANT NEWS CONTEXT FOUND IN KNOWLEDGE BASE]\n"

            for idx, article in enumerate(clean_articles, start=1):
                content = article.get("content") or article.get("text") or ""

                context += f"""
                =============================
                Article {idx}
                =============================

                Title: {article.get("title", "Untitled")}

                Source: {article.get("source", "Unknown")}

                Source Type: {article.get("source_type", "Unknown")}

                Country/Perspective: {article.get("country", "Unknown")} / {article.get("perspective_label", "unspecified")}

                Published: {article.get("publish_date", "Unknown")}

                ARTICLE URL: 
                [{article.get("source", "Source")}]
                ({article.get("url", "")})

                Content: {content[:1500]}

                END ARTICLE {idx}

                """

        # 4. Append the news context directly behind the user's prompt 
        # so Mistral reads it as part of the instructions.
        if context:
            user_message_obj["content"] = f"""
            {user_query}
            {context}
            {recent_request_instruction}
            
            Instructions: Use the provided news context above to answer the query. 
            Ensure you reproduce the URLs exactly as provided. 

            SOURCE LINK RULES:
            - Every story MUST include a working markdown source link.
            - Format links EXACTLY like:
            [Source Name](FULL_URL)

            - Never write source names without links.
            - Never summarize a story unless a URL is available.
            - Use the exact article URL provided in the context.
            - Put the source link directly underneath its matching story.

            Do not shorten or truncate URLS. 
            Return links in markdown format
            Stay neutral and avoid taking a political side.
            After answering ask 2-3 Socratic questions that won't take too long to think about but help user think critically.
            The questions should address missing perspectives, cultural context, evidence, or who benefits and loses.
            For each article you mention, include:
            - Source name
            - Source country
            - Source type
            - Perspective/Bias note

            CRITICAL FACTUALITY RULES:
            - ONLY use facts explicitly stated in the provided article context.
            - NEVER invent people, election results, quotes, laws, statistics, or relationships.
            - NEVER combine multiple articles into one story unless explicitly connected in the provided context.
            - If information is uncertain or incomplete, say so.
            - If there is not enough evidence for a claim, do not state it.
            - Use the exact URLs provided with their matching article only.
            - Never create placeholder citations or mention a source without its URL.

            - Do not call a source "unbiased." Instead say "perspective note" or "source context."

            - Do not infer additional political analysis unless clearly supported by the articles. 
            - Avoid dramatic framing or speculative interpretations. 
            - When discussing elections, laws, polling, or political figures: 
                - verify names carefully 
                - do not invent offices or election outcomes - do not invent polling numbers

            - If the user asks for recent/latest news generally, give only 3-5 diverse stories and ask what topic they want more of.
            Do not give too many stories about the same region or topic.
            Keep answers short at first, then offer to go deeper.
                        """

        # 5. Forward the updated conversation history to your Cloudflare Worker
        worker_response = requests.post(
            CLOUDFLARE_WORKER_URL, 
            json={"messages": conversation_history},
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        worker_response.raise_for_status()  # Raise an error if the worker returns a bad status
        
        # 6. Pass Mistral's final answer back to script.js
        return jsonify(worker_response.json())

    except Exception as e:
        print(f"Error in backend bridge: {e}")
        return jsonify({"message": f"Backend Error: {str(e)}"}), 500

if __name__ == "__main__":
    # Runs the server locally on http://127.0.0.1:5000
    app.run(port=5000, debug=True)