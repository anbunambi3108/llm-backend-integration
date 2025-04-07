import os
from dotenv import load_dotenv
from pinecone import Pinecone
import jwt
from flask import request
import datetime

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Connecting_LLM_VectorDB/.env"))
load_dotenv(dotenv_path)

# Load Pinecone API key
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# ✅ NEW PINECONE INITIALIZATION (CORRECT)
pc = Pinecone(api_key=PINECONE_API_KEY)

# Connect to existing index
index_name = "text-search"
if index_name not in pc.list_indexes().names():
    raise ValueError(f"Index '{index_name}' does not exist. Please create it in Pinecone console.")

index = pc.Index(index_name)

def verify_token(token):
    """
    Verifies that the incoming request is authenticated.
    Extracts the user ID from the token.
    """
    SECRET_KEY = os.getenv("JWT_SECRET", "your_default_secret_key")    
    if not token:
        return None

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded.get("user_id")
    except jwt.ExpiredSignatureError:
        print("❌ Token expired!")
        return None
    except jwt.InvalidTokenError:
        print("❌ Invalid token!")
        return None

def get_vector_search_results(user_id, query_embedding, top_k=5):
    """
    Searches only within the authenticated user's stored embeddings.
    """
    user_namespace = f"user_{user_id}"  # Restrict search to user-specific data
    results = index.query(queries=[query_embedding], top_k=top_k, namespace=user_namespace)
    return results

import datetime

def generate_token(user_id):
    """
    Generates a JWT token for testing.

    Args:
        user_id (str): The ID of the user.

    Returns:
        str: A JWT token.
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expires in 1 hour
    }
    SECRET_KEY = os.getenv("JWT_SECRET", "your_default_secret_key")
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

if __name__ == "__main__":
    test_user = "test_user_123"
    token = generate_token(test_user)
    print("✅ Your test token:", token)