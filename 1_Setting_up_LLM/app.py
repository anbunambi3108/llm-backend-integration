import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# 🔹 Load environment variables (API Key)
load_dotenv()

# 🔹 Get API key from .env file
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print("Using Groq API Key:", GROQ_API_KEY)

# 🔹 Choose the model (Supported: "mixtral-8x7b", "llama2-70b-chat", "gemma-7b")
MODEL_NAME = "llama-3.3-70b-versatile"

# 🔹 Create Flask API
app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Get user input from request
        data = request.json
        user_input = data.get("message", "")

        # Send request to Groq API (Fixed URL)
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",  # ✅ Corrected API URL
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": MODEL_NAME,  # Ensure this is a valid model (e.g., "mixtral-8x7b")
                "messages": [{"role": "user", "content": user_input}]
            }
        )

        # Parse response
        result = response.json()

        # Debugging: Print Groq's response to check for issues
        print("Groq API Response:", result)

        # Ensure 'choices' exist in response
        if "choices" not in result:
            return jsonify({"error": "Invalid response from Groq API", "details": result}), 500

        # Return AI response
        return jsonify({"response": result["choices"][0]["message"]["content"]})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the API
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
