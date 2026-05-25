# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from database import connect_db

app = Flask(__name__)
CORS(app)  # Allows your frontend script.js to communicate with this backend

CLOUDFLARE_WORKER_URL = "https://reroot-the-third.nguyen-c9.workers.dev/"

@app.route("/api/articles", methods = ["GET"])

def fetch_articles():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""SELECT title, url, source, publish_date, content
                FROM articles
                ORDER BY scraped_at DESC
                LIMIT 10
                   """)
    
    rows = cursor.fetchall()
    conn.close()

    articles = []

    for row in rows:
        articles.append({
            "title": row[0],
            "url": row[1],
            "source": row[2],
            "publish_date": row[3],
            "content": row[4]
        })

    return articles

@app.route("/api/chat", methods=["POST"])
def chat_bridge():
    try:
        data = request.json
        conversation_history = data.get("messages", [])

        if not conversation_history:
            return jsonify({"message": "Invalid history"}), 400

        # 1. Grab the very last message the user typed
        user_message_obj = conversation_history[-1]
        user_query = user_message_obj["content"]

        # 2. Query your local articles matching that query
        relevant_articles = fetch_articles()

        # 3. Format the news findings into a clear text snippet
        context = ""
        if relevant_articles:
            context = "\n\n[RELEVANT NEWS CONTEXT FOUND IN KNOWLEDGE BASE]:\n"
            for idx, article in enumerate(relevant_articles):
                context += f"Article Title: {article['title']}\n"
                context += f"URL Link: {article['url']}\n"
                context += f"Content: {article['content']}\n\n"

        # 4. Append the news context directly behind the user's prompt 
        # so Mistral reads it as part of the instructions.
        if context:
            user_message_obj["content"] = f"{user_query}{context}\nInstructions: Use the provided news context above to answer the query. Ensure you reproduce the URLs exactly as provided. Do not shorten or truncate URLS. Return links in markdown format"

        # 5. Forward the updated conversation history to your Cloudflare Worker
        worker_response = requests.post(
            CLOUDFLARE_WORKER_URL, 
            json={"messages": conversation_history},
            headers={"Content-Type": "application/json"}
        )
        
        # 6. Pass Mistral's final answer back to script.js
        return jsonify(worker_response.json())

    except Exception as e:
        print(f"Error in backend bridge: {e}")
        return jsonify({"message": f"Backend Error: {str(e)}"}), 500

if __name__ == "__main__":
    # Runs the server locally on http://127.0.0.1:5000
    app.run(port=5000, debug=True)