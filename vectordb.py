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
    
    # Chroma handles upserts safely if you specify the ID
    collection.upsert(
        documents=[article_data['text']], # The actual text that gets vectorized
        metadatas=[{
            "title": article_data['title'], 
            "url": article_data['url'],
            "publish_date": str(article_data['publish_date'])
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
    if results['documents']:
        for i in range(len(results['documents'][0])):
            formatted_articles.append({
                "text": results['documents'][0][i],
                "title": results['metadatas'][0][i]['title'],
                "url": results['metadatas'][0][i]['url']
            })
            
    return formatted_articles