from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os
import sys
from dotenv import load_dotenv
import uuid

# Load environment variables
PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../NLP_Query_Processing"))
sys.path.append(PROJECT_PATH)

# Add 5_LLM_Security to Python's module search path
SECURITY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../LLM_Security"))
sys.path.append(SECURITY_PATH)


from nlp_processing import extract_key_value
from restrict_search import get_vector_search_results, verify_token
# from encrypt_user_data import encrypt_user_data, decrypt_user_data
from anomaly_detection import detect_anomaly
from nlp_processing import build_storage_key
from nlp_processing import preprocess_query 

# Load environment variables (API keys)
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# 1. Load a pretrained Sentence Transformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

# The sentences to encode
sentences = [
    "The weather is lovely today.",
    "It's so sunny outside!",
    "He drove to the stadium.",
]

# 2. Calculate embeddings by calling model.encode()
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 384]

# 3. Calculate the embedding similarities
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[1.0000, 0.6660, 0.1046],
#         [0.6660, 1.0000, 0.1411],
#         [0.1046, 0.1411, 1.0000]])

# 4. Connect to Pinecone and store embeddings
# Load Hugging Face embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY) 
index_name = "text-search"

# Connect to existing Pinecone index
if index_name not in pc.list_indexes().names():
    raise ValueError(f"Index '{index_name}' does not exist. Please create it in the Pinecone console.")

index = pc.Index(index_name)

def embed_text(text):
    """Generate embeddings."""
    return model.encode(text).tolist()

def store_text(user, key, value, relation=None):
    """
    Stores extracted key-value pairs in Pinecone securely.

    Args:
        user (str): User identifier to store personalized data.
        key (str): The extracted key for the data.
        value (str): The value to store.

    Returns:
        None
    """
    if not key or not value:
        print("⚠️ Invalid key-value pair!")
        return
    
    stored_value = value
    storage_key = build_storage_key(key, relation)
    vector_id = f"{user}_{key}"  # Create a unique ID per user
    doc_id = f"{key}_{uuid.uuid4()}"  # Generate a unique ID for the document
    vector_id = doc_id
    full_key = f"{relation} {key}".strip() if relation else key
    embedding = embed_text(full_key)  # ✅ Store only the key for retrieval

    vectors = [(vector_id, embedding, {
        "value": stored_value, 
        "user": user,
        "relation": relation or "",
        "key": storage_key
        })]
    print("DEBUG: Upserting into Pinecone with metadata:", vectors)
    index.upsert(vectors=vectors, namespace=f"user_{user}") # ✅ Add namespace

    print(f"Stored: '{key}' for user: {user}")
    print(f"relation: {relation} for user: {user}")


def search_text(user, query, top_k=1):
    """
    Searches for a stored key and returns only the decrypted value.

    - Ensures the request is authenticated.
    - Limits search to the correct user's namespace.
    - Detects suspicious activity before retrieving data.

    Args:
        user (str): The user making the request.
        query (str): The user's search query.
        top_k (int): Number of top results to return.

    Returns:
        str: The stored value if found, otherwise None.
    """
    print(f"[DEBUG] Searching for query: '{query}' by user: '{user}'")

    # Detect anomalies (e.g., excessive queries)
    anomaly_alert = detect_anomaly(user)
    if anomaly_alert != "Normal activity.":
        return {"error": anomaly_alert}, 429

    # Securely query Pinecone
    cleaned_query = preprocess_query(query)
    print(f"[DEBUG] Cleaned query: '{cleaned_query}'")
    query_embedding = embed_text(cleaned_query)
    print(f"[DEBUG] Generated embedding for query.")

    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True, namespace=f"user_{user}")
    print(f"[DEBUG] Raw Pinecone matches: {results.get('matches', [])}")

    SIMILARITY_THRESHOLD = 0.5

    if results and results["matches"]:
        for match in results["matches"]:
            print(f"[DEBUG] Match metadata: {match['metadata']}")

            if match["score"] >= SIMILARITY_THRESHOLD and match["metadata"].get("user") == user: # ✅ Ensure result belongs to correct user
                # encrypted_value = match["metadata"].get("value")  
                # decrypted_value = decrypt_user_data(user, encrypted_value)  # 🔐 Decrypt before returning
                stored_value = match["metadata"].get("value")
                print(f"[DEBUG] Decrypted value: {stored_value}")
                return stored_value, match["score"]
            
    print("[DEBUG] No matches found or user mismatch.")
    return None, None

if __name__ == "__main__":
    # Store sample texts (only needed once)
    sample_data = [
        ("Passport", "X12345678, Name: John Doe, Date of Birth: 15th July 1990, Expiry: 12th Dec 2030"),
        ("Passport", "Y98765432, Name: Alice Smith, Date of Birth: 22nd March 1985, Expiry: 8th Aug 2028"),
        ("Passport", "Z55511122, Name: Robert Johnson, Date of Birth: 5th May 1975, Expiry: 20th Nov 2025")
    ]
    
    # Ask user for authentication token
    token = input("Enter your token: ").strip()
    user_id = verify_token(token)

    if not user_id:
        print("\n❌ Authentication failed! Access denied.")
    else:
        # Store text securely (Only needed once per user)
        for key, text in sample_data:
            store_text(user_id, key, text)

        print("\nPlease enter your question below:")
        query = input("> ").strip()  # Takes user input
        result = search_text(user_id, query)

        if result and result[0]:  # Ensure result_text is not None
            result_text, score = result
            print(f"\n✅ Best match: {result_text}\n🔹 Score: {score:.4f}")
        else:
            print("\n❌ No match found.")

