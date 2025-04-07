import os
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from dotenv import load_dotenv
import re


# Download necessary NLP resources
nltk.download("punkt")
nltk.download("stopwords")

# Load environment variables
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Setting_up_LLM/.env"))
load_dotenv(env_path)

# Fetch API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def preprocess_query(query):
    """
    Cleans and preprocesses user input by removing stopwords and punctuation.

    Args:
        query (str): The user's input text.

    Returns:
        str: Processed text with only important words.
    """
    query = re.sub(r"\b(\w+)'s\b", r"\1", query)
    query = query.lower()  # Convert to lowercase
    query = query.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
    words = word_tokenize(query)  # Tokenize
    filtered_words = [word for word in words if word not in stopwords.words("english")]  # Remove stopwords
    return " ".join(filtered_words)  # Convert list back to string

def extract_key_value(user_input):
    """
    Extracts key-value-relation triples from user input dynamically.

    Examples:
        "My wife's SSN is 987-65-4321" → ("ssn", "987-65-4321", "wife")
        "Dad's birthday is June 4th" → ("birthday", "June 4th", "dad")
    """
    print(f"📝 DEBUG: Raw User Input: {user_input}")

    cleaned_input = user_input.replace("@store", "").replace("@update", "").replace("@delete", "").strip()
    if cleaned_input.lower().startswith("my "):
        cleaned_input = cleaned_input[3:].strip()
    print(f"📝 DEBUG: Cleaned Input: {cleaned_input}")

    key_value_relation = []

    statements = re.split(r"\s+and\s+", cleaned_input)

    for statement in statements:
        match = re.search(r"(.*?)(?:is|to|=)\s*(.*)", statement, re.IGNORECASE)
        if match:
            raw_key = match.group(1).strip().lower()
            value = match.group(2).strip()

            relation = None
            key = raw_key

            # Try to extract relationship from possessive (e.g. "wife's SSN")
            possessive_match = re.match(r"(\w+)'s\s+(.*)", raw_key)
            if possessive_match:
                relation = possessive_match.group(1).lower()  # "wife"
                key = possessive_match.group(2).strip()       # "ssn"

            print(f"📝 DEBUG: Extracted → key: {key}, value: {value}, relation: {relation}")
            key_value_relation.append((key, value, relation))

    return key_value_relation if key_value_relation else None

def extract_key_for_retrieval(user_input):
    """
    Extracts key and relation for retrieval (e.g., 'what is my wife's passport number?').
    Returns (key, relation) tuple.
    """
    cleaned = user_input.strip().lower()

    # Remove leading question words, helpers, and 'my'
    cleaned = re.sub(r"^(what's|what|tell me|when does|where is|how does|who has|can you|do you know)[\s,]+", '', cleaned)
    cleaned = re.sub(r'^my\s+', '', cleaned)

    # Try to extract relation from possessive (e.g., "wife's passport")
    possessive_match = re.match(r"(\w+)'s\s+(.*)", cleaned)
    if possessive_match:
        relation = possessive_match.group(1)
        key = possessive_match.group(2)
    else:
        key = cleaned
        relation = None

    # Additional cleanup: strip out junk and trailing punctuation
    key = re.sub(r'^(is|my|the)\s+', '', key, flags=re.IGNORECASE).strip()
    key = key.rstrip('?.!').strip()

    return key, relation


def clean_query_text(query):
    """
    Cleans query text by removing unnecessary words like 'my'
    and ensuring proper formatting for responses.

    Args:
        query (str): The input text (e.g., "my cousin's phone number")

    Returns:
        str: Cleaned and natural query text (e.g., "cousin's phone number")
    """
    query = query.strip().lower()
    if query.lower().startswith("my "):
        query = query[3:]
    query=query.replace("'s","")
    return query.strip()

def build_storage_key(key, relation=None):
    """
    Combines relation and key to form a standardized storage key.
    For example, "passport number" + "wife" => "wife passport number"
    """
    key = key.strip().lower()
    if relation:
        return f"{relation.strip().lower()} {key}"
    return key

def extract_relation_and_key(query):
    """
    Extracts relation and key from user input.
    Example: "my wife's passport number" → ("wife", "passport number")
    """
    match = re.match(r"(?:my\s+)?(\w+)'s\s+(.*)", query.strip(), re.IGNORECASE)
    if match:
        return match.group(1).lower(), match.group(2).lower()
    return None, query.lower()

def to_possessive(phrase):
    """
    Converts the first word (assumed to be a relation) into possessive form.
    E.g., 'wife passport number' → 'wife's passport number'
    
    If already possessive, returns as is.
    """
    words = phrase.strip().split()
    if not words:
        return phrase

    # Don't double-possess
    if words[0].endswith("'s"):
        return phrase

    words[0] = words[0] + "'s"
    return " ".join(words)