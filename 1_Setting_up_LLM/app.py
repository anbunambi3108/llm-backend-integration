import os
import sys
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone

# Add the path to the NLP processing module
nlp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../2_NLP_Query_Processing"))
sys.path.append(nlp_path)

# Import NLP components
from nlp_processing import preprocess_query, extract_key_value  
from crud_operations import detect_intent  
from query_handler import retrieve_value, find_closest_key  
from relationship_mapping import get_relationship, add_relationship, update_relationship, delete_relationship 
from relationship_api import relationship_app


# Load environment variables (API Key)
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY") # API Key for LLM
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")  # API Key for Pinecone

# Choose the model
MODEL_NAME = "llama-3.3-70b-versatile"
# Load Sentence Transformer model for embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")


# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "text-search"

# Connect to Pinecone Index
if index_name not in pc.list_indexes().names():
    raise ValueError(f"Index '{index_name}' does not exist. Please create it in Pinecone.")

index = pc.Index(index_name)


# Create Flask API
app = Flask(__name__)

# 🔹 Transition to MongoDB
# Replace this in-memory dictionary with MongoDB queries
# Example: Use collection.insert_one() to store data instead of using user_memory
user_memory = {}  # Temporary in-memory storage (to be replaced)

@app.route("/chat", methods=["POST"])
def chat():
    """
    Handles user queries by detecting intent and managing user memory.
    
    - If intent is 'store_memory', saves key-value pairs.
    - If intent is 'update_memory', updates stored data.
    - If intent is 'delete_memory', removes stored entries.
    - If intent is 'retrieve_memory', fetches stored details OR falls back to LLM.
    
    Returns:
        JSON response based on detected intent or AI model output.
    """
    try:
        # Extract request data
        data = request.json
        user_input = data.get("message", "")
        user = data.get("user", "")

        # Check for missing inputs
        if not user_input or not user:
            return jsonify({"error": "Missing message or user"}), 400

        # Detect user intent
        user_intent = detect_intent(user_input)
        print("User Memory:", user_memory)  # ✅ Debugging: Check if data is being stored

        # Handle storing memory
        if user_intent == "store_memory":
            key_value_pairs = extract_key_value(user_input)  # ✅ Extract multiple key-value pairs
            print(f"📝 Extracted Key-Value Pairs: {key_value_pairs}")

            if not key_value_pairs:
                return jsonify({"error": "Invalid format. Use '@store key is value'"}), 400

            if user not in user_memory:
                user_memory[user] = {}

            for key, value in key_value_pairs:
                if key not in user_memory[user]:
                    user_memory[user][key] = []
                user_memory[user][key].append(value)

            print(f"✅ Updated User Memory after Storage: {user_memory}")
            return jsonify({"response": f"I have stored {', '.join([f'{k}: {v}' for k, v in key_value_pairs])}."})

        # Handle updating memory (overwrite existing values)
        elif user_intent == "update_memory":
            key_value_pairs = extract_key_value(user_input)  # ✅ Extract multiple key-value pairs
            print(f"📝 Extracted Key-Value Pairs for Update: {key_value_pairs}")

            if not key_value_pairs:
                return jsonify({"error": "Invalid format. Use '@update key is value'"}), 400

            if user not in user_memory:
                return jsonify({"response": "No stored data found for this user."})
            
            updated_keys = []
            print(f"🔍 Stored Keys for User {user}: {list(user_memory[user].keys())}")
            not_found_keys = []

            for key, value in key_value_pairs:
                print(f"🔍 Standardized Key for Update: {key}")
                print(f"🔍 Stored Keys for User {user} after Standardization: {list(user_memory[user].keys())}")
                
                if key in user_memory[user]:
                    user_memory[user][key] = [value]  # ✅ Overwrite previous value
                    updated_keys.append(key)
                    print(f"✅ Updated {key}: {user_memory[user][key]}")
                    print(f"📝 Updated Memory for User {user}: {user_memory[user]}")
                    continue

                # ✅ If the exact key isn't found, try to standardize it
                standardized_key = get_standardized_key(key)
                print(f"🔍 Standardized Key for Update: {standardized_key}")

                closest_match = find_closest_key(standardized_key, user_memory[user].keys())
                print(f"🔍 Closest Match for Standardized Key: {closest_match}")

                if closest_match:
                    user_memory[user][closest_match] = [value]  # ✅ Overwrite previous value
                    updated_keys.append(closest_match)
                    print(f"✅ Updated {closest_match}: {user_memory[user][closest_match]}")
                    print(f"📝 Updated Memory for User {user}: {user_memory[user]}") 

                # if standardized_key in user_memory[user]:
                #     user_memory[user][standardized_key] = [value]  # ✅ Overwrite previous value
                #     updated_keys.append(standardized_key)
                #     print(f"✅ Updated {standardized_key}: {user_memory[user][standardized_key]}")
                #     print(f"📝 Updated Memory for User {user}: {user_memory[user]}")
                else:
                    not_found_keys.append(key)  

            response_message = f"I have updated {', '.join(updated_keys)}." if updated_keys else "I couldn't find any keys to update."

            if not_found_keys:
                response_message += f" However, I couldn't find {', '.join(not_found_keys)}."

            return jsonify({"response": response_message})

        # Handle deleting memory
        elif user_intent == "delete_memory":
            key_value_pairs = extract_key_value(user_input)  # ✅ Extract multiple key-value pairs
            print(f"🗑️ Extracted Keys for Deletion: {key_value_pairs}")

            if not key_value_pairs:
                return jsonify({"error": "Invalid format. Use '@delete key'"}), 400

            if user not in user_memory:
                return jsonify({"response": "No stored data found for this user."})

            deleted_keys = []
            not_found_keys = []

            for key, _ in key_value_pairs:  # ✅ Only extract the key, value is ignored
                print(f"🔍 Checking for deletion: {key}") 
                if key is None:
                    continue
                if key in user_memory[user]:
                    del user_memory[user][key]
                    deleted_keys.append(key)
                    print(f"✅ Deleted Key: {key}")
                    print(f"✅ Deleted Key: {key} from User {user} Memory")
                    continue

                # ✅ If the exact key isn't found, try to standardize it
                standardized_key = get_standardized_key(key)
                print(f"🔍 Checking for deletion: {standardized_key}")

                closest_match = find_closest_key(standardized_key, user_memory[user].keys())
                print(f"🔍 Closest Match for Standardized Key: {closest_match}")

                if closest_match:
                    del user_memory[user][closest_match]
                    deleted_keys.append(closest_match)
                    print(f"✅ Deleted Key: {closest_match}")
                    print(f"✅ Deleted Key: {closest_match} from User {user} Memory")
                    # continue

                # if standardized_key in user_memory[user]:
                #     del user_memory[user][standardized_key]
                #     deleted_keys.append(standardized_key)
                #     print(f"✅ Deleted Key: {standardized_key}")
                #     print(f"✅ Deleted Key: {standardized_key} from User {user} Memory")
                else:
                    not_found_keys.append(standardized_key)

            response_message = f"I have deleted {', '.join(deleted_keys)}." if deleted_keys else "I couldn't find any keys to delete."
            # if deleted_keys:
            #     response_message = f"I have deleted {', '.join(deleted_keys)}."
            # else:
            #     response_message = "I couldn't find any keys to delete."

            if not_found_keys:
                response_message += f" However, I couldn't find {', '.join(not_found_keys)}."

            print(f"📝 Updated Memory after Deletion: {user_memory}")
            return jsonify({"response": response_message})

        # ✅ Updated: Handle retrieving memory dynamically
        elif user_intent == "retrieve_memory":
            response = retrieve_value(user, user_input, user_memory)  # ✅ Calls the function from query_handler.py
            print("User Memory:", user_memory)  # ✅ Debugging: Check if data is being stored
            print(f"Retrieval Response: {response}")  # ✅ Debug retrieval output

            # ✅ Updated: If retrieval fails, preprocess query and call LLM fallback
            if "couldn't find" in response.lower() and "I have stored" not in response:  
                print("Retrieval Failed. Calling LLM Fallback...")
                cleaned_query = preprocess_query(user_input)  # ✅ Ensures LLM gets a clean input
                print(f"Preprocessed Query: {cleaned_query}")
                response = requests.post("https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": "llama-3.3-70b-versatile", 
                    "messages": [
                        {"role": "system", "content": "You are an assistant that retrieves stored personal data. Always check memory before responding. If memory is missing, ask the user if they want to store it."},
                        {"role": "user", "content": user_input}
                    ]})
                result = response.json()
                if "choices" in result:
                    return jsonify({"response": result["choices"][0]["message"]["content"]})

                return jsonify({"response": "I'm not sure about that. Would you like to add it to your memory?"})
            
            return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the API
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)