import os
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from dotenv import load_dotenv
import re

from relationship_mapping import get_standardized_key

# Download necessary NLP resources
nltk.download("punkt")
nltk.download("stopwords")

# Load environment variables
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../1_Setting_up_LLM/.env"))
load_dotenv(env_path)

# Fetch API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def clean_query_text(query):
    """
    Cleans query text by removing unnecessary words like 'my'
    and ensuring proper formatting for responses.

    Args:
        query (str): The input text (e.g., "my cousin's phone number")

    Returns:
        str: Cleaned and natural query text (e.g., "cousin's phone number")
    """
    query = query.strip()

    # ✅ Remove "my " from the start to avoid awkward responses
    if query.lower().startswith("my "):
        query = query[3:]  # Remove first 3 characters ("my ")

    return query

def preprocess_query(query):
    """
    Cleans and preprocesses user input by removing stopwords and punctuation.

    Args:
        query (str): The user's input text.

    Returns:
        str: Processed text with only important words.
    """
    query = query.lower()  # Convert to lowercase
    query = query.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
    words = word_tokenize(query)  # Tokenize
    filtered_words = [word for word in words if word not in stopwords.words("english")]  # Remove stopwords
    return " ".join(filtered_words)  # Convert list back to string

def extract_key_value(user_input):
    """
    Extracts key-value pairs dynamically, including handling '@delete' requests properly.
    """
    print(f"📝 DEBUG: Raw User Input: {user_input}")  

    cleaned_input = user_input.replace("@store", "").replace("@update", "").replace("@delete", "").strip()
    print(f"📝 DEBUG: Cleaned Input: {cleaned_input}")  

    key_value_pairs = []
    # ✅ Ensure 'her' is replaced correctly
    if "her " in cleaned_input and "wife" in cleaned_input:
        cleaned_input = cleaned_input.replace("her ", "wife's ")
    # ✅ Special handling for delete commands (no key-value pairs, only keys)
    if user_input.startswith("@delete"):
        keys_to_delete = re.split(r"\s+and\s+", cleaned_input)
        # key_value_pairs = [(key.strip(), None) for key in keys_to_delete]
        key_value_pairs = [(get_standardized_key(key.strip()), None) for key in keys_to_delete]
        print(f"✅ DEBUG: Extracted Keys for Deletion: {key_value_pairs}")  
        return key_value_pairs  

    # ✅ Normal key-value extraction for store/update
    statements = re.split(r"\s+and\s+", cleaned_input)
    for statement in statements:
        match = re.search(r"(.*?)(?:is|to|=)\s*(.*)", statement, re.IGNORECASE)
        if match:
            key = match.group(1).strip().lower()
            value = match.group(2).strip()
            print(f"📝 DEBUG: Extracted Key: {key}, Value: {value}")  
            key_value_pairs.append((key, value))

    print(f"✅ DEBUG: Final Extracted Key-Value Pairs: {key_value_pairs}")
    return key_value_pairs if key_value_pairs else None
