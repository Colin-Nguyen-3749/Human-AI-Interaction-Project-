import chromadb
from chromadb.utils import embedding_functions

# 1. Initialize the local persistent client
# This creates a folder named 'chroma_data' in your project directory
chroma_client = chromadb.PersistentClient(path="./chroma_data")

# 2. Define an embedding function using a lightweight local model
# This model will run on your machine to convert text into semantic vectors
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# 3. Get or create a collection (similar to a SQL table or Firestore collection)
collection = chroma_client.get_or_create_collection(
    name="news_knowledge_base", 
    embedding_function=embedding_func
)

def save_to_vector_db(article_data):
    """Inserts an article into the local vector database."""
    # Use the URL as a unique ID to prevent duplicates
    doc_id = article_data['url']

    article_text = article_data.get("content") or article_data.get("text")

    # Chroma handles upserts safely if you specify the ID
    collection.upsert(
        documents=[article_text], # The actual text that gets vectorized
        metadatas=[{
            "title": article_data.get("title", "Untitled"),
            "url": article_data.get("url", ""),
            "publish_date": str(article_data.get("publish_date", "Unknown")),
            "source": article_data.get("source", "Unknown"),
            "country": article_data.get("country", "Unknown"),
            "language": article_data.get("language", "en"),
            "source_type": article_data.get("source_type", "news"),
            "perspective_label": article_data.get("perspective_label", "unspecified"),
            "category": article_data.get("category", "news")
        }], # Metadata you want to pass to the chatbot along with the text
        ids=[doc_id]
    )

def query_knowledge_base(user_query, limit=3):
    """Performs a semantic search and returns the most relevant articles."""
    results = collection.query(
        query_texts=[user_query],
        n_results=limit
    )
    
    # Reformatting the output into a clean, readable dictionary structure
    formatted_articles = []

    if not results or not results.get("documents"):
        return formatted_articles

    documents = results.get("documents", [0])
    metadata = results.get("metadatas", [0])

    for i in range(len(documents)):
        metadata = metadata[i]

        formatted_articles.append({
            "text": documents[i],
            "title": metadata.get("title", "Untitled"),
            "url": metadata.get("url", ""),
            "publish_date": metadata.get("publish_date", "Unknown"),
            "source": metadata.get("source", "Unknown"),
            "country": metadata.get("country", "Unknown"),
            "language": metadata.get("language", "en"),
            "source_type": metadata.get("source_type", "news"),
            "perspective_label": metadata.get("perspective_label", "unspecified"),
            "category": metadata.get("category", "news")
        })

    return formatted_articles