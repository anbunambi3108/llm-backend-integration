from flask import Blueprint, request, jsonify
from relationship_mapping import get_relationship, add_relationship, update_relationship, delete_relationship

# ✅ Use Blueprint instead of Flask instance
relationship_api = Blueprint("relationship_api", __name__)

@relationship_api.route("/relationship/add", methods=["POST"])
def add_new_relationship():
    """API to add a new relationship
    
    This function accepts a JSON payload with two key-value pairs:
    - "relationship": the name of the relationship (e.g. "brother", "sister", etc.)
    - "category": the category of the relationship (e.g. "family", "spouse", etc.)
    
    If the payload is missing either of these two key-value pairs, the function
    will return a JSON response with a 400 status code and an error message.
    
    If the payload is valid, the function will call the add_relationship()
    function from the relationship_mapping module to add the relationship to
    both the database and in-memory dictionary. The function will then return
    a JSON response with a message indicating the relationship was added.
    """
    data = request.get_json()
    
    try:
        # Extract the relationship and category from the JSON payload
        relationship = data["relationship"]
        category = data["category"]
    except KeyError:
        # If the payload is missing either key, return an error message
        return jsonify({"error": "Missing relationship or category"}), 400
    
    # Call the add_relationship() function to add the relationship to the database and in-memory dictionary
    add_relationship(relationship, category)
    
    # Return a JSON response with a message indicating the relationship was added
    return jsonify({"message": f"Added '{relationship}' as '{category}'"})

@relationship_api.route("/relationship/get", methods=["GET"])
def get_relationship_category():
    """
    API to get the category of a relationship
    
    This function is called when a GET request is made to the /relationship/get endpoint.
    The function expects a query parameter named "relationship" to be passed in the
    request. If the parameter is missing, the function will return a JSON response
    with a 400 status code and an error message.
    
    If the parameter is present, the function will call the get_relationship()
    function from the relationship_mapping module to retrieve the category of
    the relationship. The function will then return a JSON response with the
    relationship and its category.
    """
    # Get the relationship from the query parameters
    relationship = request.args.get("relationship")
    
    # If the relationship is missing, return an error message
    if not relationship:
        return jsonify({"error": "Missing relationship"}), 400
    
    # Call the get_relationship() function to get the category of the relationship
    category = get_relationship(relationship)
    
    # Return a JSON response with the relationship and its category
    return jsonify({"relationship": relationship, "category": category})

@relationship_api.route("/relationship/update", methods=["PUT"])
def update_existing_relationship():
    """API to update an existing relationship
    
    This function accepts a JSON payload with two key-value pairs:
    - "relationship": the name of the relationship to update (e.g. "brother", "sister", etc.)
    - "new_category": the new category of the relationship (e.g. "family", "spouse", etc.)
    
    If the payload is missing either of these two key-value pairs, the function
    will return a JSON response with a 400 status code and an error message.
    
    If the payload is valid, the function will call the update_relationship()
    function from the relationship_mapping module to update the relationship in
    both the database and in-memory dictionary. The function will then return
    a JSON response with a message indicating the relationship was updated.
    """
    data = request.get_json()
    
    # Check if the payload contains both keys
    if "relationship" not in data or "new_category" not in data:
        return jsonify({"error": "Missing relationship or new_category"}), 400
    
    # Call the update_relationship() function to update the relationship in the database and in-memory dictionary
    update_relationship(data["relationship"], data["new_category"])
    
    # Return a JSON response with a message indicating the relationship was updated
    return jsonify({"message": f"Updated '{data['relationship']}' to '{data['new_category']}'"})

@relationship_api.route("/relationship/delete", methods=["DELETE"])
def delete_existing_relationship():
    """API to delete a relationship

    This function expects a JSON payload with a single key-value pair:
    - "relationship": the name of the relationship to delete (e.g. "brother", "sister", etc.)

    If the payload is missing the "relationship" key, the function will return 
    a JSON response with a 400 status code and an error message.

    If the payload is valid, the function will call the delete_relationship()
    function from the relationship_mapping module to remove the relationship
    from both the database and the in-memory dictionary. The function will then
    return a JSON response with a message indicating the relationship was deleted.
    """
    # Extract the JSON payload from the request
    data = request.get_json()
    
    # Attempt to retrieve the "relationship" value from the JSON payload
    relationship = data.get("relationship")
    
    # Check if the "relationship" key exists in the JSON payload
    if relationship:
        # If the relationship exists, call the delete_relationship function
        # to remove it from the database and in-memory dictionary
        delete_relationship(relationship)
        
        # Return a JSON response confirming the deletion of the relationship
        return jsonify({"message": f"Deleted relationship '{relationship}'"})
    else:
        # If the "relationship" key is missing, return an error message
        return jsonify({"error": "Missing relationship"}), 400
