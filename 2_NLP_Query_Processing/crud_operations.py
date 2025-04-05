import spacy

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Define intent categories based on key action words
intent_keywords = {
    "retrieve_memory": ["what", "tell", "show", "give", "fetch"],
    "store_memory": ["@store"],  # Store extracted information
    "update_memory": ["@update"],  # Overwrite existing values
    "delete_memory": ["@delete"]  # Remove stored values
}

def detect_intent(query):
    """
    Detects user intent based on keywords in their query.
    
    Args:
        query (str): User's input text.

    Returns:
        str: The detected intent (store_memory, update_memory, delete_memory, retrieve_memory, or unknown).
    """
    doc = nlp(query.lower())  # Convert text to lowercase for uniform processing

    # Check for command-based keywords (@store, @update, @delete)
    for intent, keywords in intent_keywords.items():
        if any(keyword in query for keyword in keywords):
            return intent  # Return matched intent

    # If no command is found, assume it's a retrieval query (retrieve_memory)
    return "retrieve_memory"  # By default, assume the user wants to retrieve stored data