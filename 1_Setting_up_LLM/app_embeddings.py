from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import os
import sys
import re

# Add path to NLP and VectorDB modules
nlp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../2_NLP_Query_Processing"))
sys.path.append(nlp_path)

vectordb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../3_Connecting_LLM_VectorDB"))
sys.path.append(vectordb_path)

# Import NLP components
from nlp_processing import preprocess_query, extract_key_value, clean_query_text, build_storage_key, extract_key_for_retrieval
from crud_operations import detect_intent

# Import storage and search logic
from vectordb import store_text, search_text

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    """
    Handles user messages, determines intent, stores or retrieves info via VectorDB.
    """
    try:
        data = request.get_json()
        raw_input = data.get("message", "").strip()
        user = data.get("user", "").strip()

        if not raw_input or not user:
            return jsonify({"error": "Missing message or user"}), 400

        intent = detect_intent(raw_input)
        print("Intent detected:", intent)

        query = preprocess_query(raw_input)
        user_input = raw_input  # for clarity

        # ✅ STORE
        if intent == "store_memory":
            key_value_pairs = extract_key_value(user_input)
            if not key_value_pairs:
                return jsonify({"error": "No valid key-value pair found"}), 400

            formatted_responses = []
            for key, value, relation in key_value_pairs:
                cleaned_key = clean_query_text(key)
                full_key = build_storage_key(cleaned_key, relation)
                print(f"Storing: '{full_key}' → '{value}' for user: {user}")
                store_text(user, full_key, value, relation)
                formatted_responses.append(f"I have stored your {full_key}: {value}.")

            return jsonify({"response": " ".join(formatted_responses)})

        # ✅ RETRIEVE
        if intent == "retrieve_memory":
            key, relation = extract_key_for_retrieval(user_input)
            cleaned_key = clean_query_text(key)
            full_key = build_storage_key(cleaned_key, relation)
            readable_key = f"{relation}'s {cleaned_key}" if relation else cleaned_key

            print(f"Searching for: {full_key} for user: {user}")
            result_text, score = search_text(user, full_key)

            if result_text:
                return jsonify({
                    "response": f"Your {readable_key} is {result_text}.",
                    "score": score
                })
            else:
                return jsonify({"response": "I couldn't find that information."})

        return jsonify({"error": "Unknown intent"}), 400

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
