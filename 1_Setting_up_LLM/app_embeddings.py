# from flask import Flask, request, jsonify
# from dotenv import load_dotenv
# import requests
# import os
# import sys

# # Add the path to the NLP processing module
# nlp_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../2_NLP_Query_Processing"))
# sys.path.append(nlp_path)
# # Add the path to vectordb.py
# vectordb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../3_Connecting_LLM_VectorDB"))
# sys.path.append(vectordb_path)

# # Import NLP components
# from nlp_processing import preprocess_query,extract_key_value, clean_query_text, extract_relation_and_key,to_possessive
# from nlp_processing import *
# from crud_operations import detect_intent  
# from query_handler import retrieve_value
# from vectordb import store_text, search_text  

# # def format_query(query):
# #     """
# #     Standardizes queries by replacing relationship terms with their general category.
# #     """
# #     # Use a set lookup for faster results
# #     standardized_query = " ".join(
# #         get_relationship(word) if get_relationship(word) != "unknown" else word
# #         for word in query.split()
# #     )
# #     return standardized_query

# # Load environment variables
# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# app = Flask(__name__)

# @app.route("/chat", methods=["POST"])
# def chat():
#     """Handles user queries and retrieves data from VectorDB (Pinecone)."""
#     try:
#         print("Received:", request.json)
#         data = request.get_json()  # Ensure JSON is parsed correctly
#         user_input = data.get("message", "").strip()  # Extract message
#         raw_input = data.get("message", "").strip()
#         user = data.get("user", "").strip()  # Extract user

#         if not user_input or not user:
#             return jsonify({"error": "Missing message or user"}), 400

#         print("Preprocessing query:", user_input)
#         query = preprocess_query(user_input)
        
        

#         # ✅ Step 1: Detect the user intent
#         intent = detect_intent(user_input)  
#         print("Intent detected:", intent)
#         print("Query:", query)
#         query = preprocess_query(raw_input)
#         user_input = raw_input
#         print("Preprocessed query:", query)
#         print("User Input:", user_input)


#         # ✅ Step 2: Handle storing intent (@store)
#         if intent == "store_memory":
#             key_value_pairs = extract_key_value(user_input)

#             if not key_value_pairs:
#                 return jsonify({"error": "No valid key-value pair found"}), 400

#             formatted_responses = []

#             for key, value, relation in key_value_pairs:
#                 cleaned_key = clean_query_text(key)
#                 # full_key = f"{relation} {cleaned_key}" if relation else cleaned_key
                
#                 print(f"Storing: '{cleaned_key}' → '{value}' for user: {user}")
#                 store_text(user, cleaned_key, value, relation)

#                 # formatted_responses.append(f"I have stored your {cleaned_key}: {value}.")
#                 if relation:
#                     readable_key = f"I have stored your {relation}'s {cleaned_key}."
#                 else:
#                     readable_key = f"I have stored your {cleaned_key}."

#                 formatted_responses.append(f"I have stored {readable_key}.")

#         # ✅ Step 3: Handle retrieval intent
#         if intent == "retrieve_memory":
#             relation, raw_key = extract_relation_and_key(user_input)
#             key_value_pairs = extract_key_value(user_input)

#             if key_value_pairs:
#                 key, _, relation = key_value_pairs[0]
#                 cleaned_key = clean_query_text(key)
#                 full_key = build_storage_key(cleaned_key, relation)
#             else:
#                 full_key = clean_query_text(preprocess_query(user_input))
#             print(f"Searching for: {full_key} for user: {user}")
#             result_text, score = search_text(user, full_key)

#             if result_text:
#                 format_response = f"Your {full_key} is {result_text}."
#                 return jsonify({"response": format_response, "score": score})
#             else:
#                 return jsonify({"response": "I couldn't find that information."})



#             full_key = f"{relation} {raw_key}" if relation else raw_key
#             cleaned_query = clean_query_text(full_key)

#             print(f"Searching for: {cleaned_query} for user: {user}")
#             result_text, score = search_text(user, cleaned_query)

#             if result_text:
#                 print("Found:", result_text)
#                 readable_query = to_possessive(cleaned_query)
#                 cleaned_key = build_storage_key(clean_query_text(key), relation)
#                 formatted_response = f"Your {cleaned_key} is {result_text}."
#                 formatted_response = f"Your {cleaned_query} is {result_text}."
#                 return jsonify({"response": formatted_response, "score": score})

#             # key_value_pairs = extract_key_value(user_input)
#             # if key_value_pairs:
#                 # key, _, relation = key_value_pairs[0]
#                 # cleaned_query = build_storage_key(clean_query_text(key), relation)

#             # print(f"Searching for: {cleaned_query} for user: {user}")
#             # result_text, score = search_text(cleaned_query, user)

#             # if result_text:
#                 # print("Found:", result_text)
#                 # formatted_response = f"Your {cleaned_query} is {result_text}."
#                 # return jsonify({"response": formatted_response, "score": score})

#             # ✅ Step 4: Handle fallback intent
#             if intent == "fallback":
#                 fallback_response = retrieve_value(query)
#                 return jsonify({"response": fallback_response})

#             # ✅ Step 5: Handle fallback intent
#             print("No match found.")
#             return jsonify({"response": "I couldn't find that information."})

#         return jsonify({"error": "Unknown intent"}), 400

#     except Exception as e:
#         print("Error:", str(e))
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":  
#     app.run(host="0.0.0.0", port=5000, debug=True)

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
