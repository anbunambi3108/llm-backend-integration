from difflib import get_close_matches
from nlp_processing import clean_query_text

def find_closest_key(user_input, stored_keys):
    """
    Finds the closest matching key from stored user memory.

    Args:
        user_input (str): The key the user is looking for.
        stored_keys (list): List of all available keys in memory.

    Returns:
        str: The closest matching key or None if no match is found.
    """
    user_input = user_input.lower()

    # ✅ Try exact match first
    if user_input in stored_keys:
        return user_input

    # ✅ Try fuzzy matching
    matches = get_close_matches(user_input, stored_keys, n=1, cutoff=0.5)

    if matches:
        return matches[0]  # ✅ Return the best match
    return None  # ✅ No match found

def retrieve_value(user, user_input, user_memory):
    """
    Retrieves the stored value dynamically and ensures correct relationship mapping.
    """
    if user not in user_memory:
        return "I don't have any stored information for you."

    standardized_key = get_standardized_key(user_input)  # ✅ Standardize before searching
    standardized_key = clean_query_text(user_input)

    print(f"🔍 DEBUG: Standardized Key - {standardized_key}")
    print(f"🔍 DEBUG: Stored Keys for {user} - {list(user_memory[user].keys())}")

    # ✅ Ensure correct key search
    if standardized_key in user_memory[user]:
        return f"{standardized_key}: {', '.join(user_memory[user][standardized_key])}"

    # ✅ Use fuzzy matching if direct lookup fails
    closest_match = find_closest_key(standardized_key, user_memory[user].keys())
    if closest_match:
        return f"{closest_match}: {', '.join(user_memory[user][closest_match])}"

    return "I couldn't find that information in memory."

def get_standardized_key(query):
    # Simply clean and standardize the query text
    return clean_query_text(query)