import sqlite3

def get_standardized_key(query):
    """
    Converts relationship-based queries into their standard keys dynamically.

    Args:
        query (str): The user’s query containing relationship terms.

    Returns:
        str: The standardized key if found, else None.
    """
    query_lower = query.lower()

    # ✅ Direct lookup in relationship_map
    for phrase, mapped_key in relationship_map.items():
        if phrase in query_lower:
            return mapped_key

    return None  # No match found

# ✅ Step 1: In-Memory Dictionary for Fast Lookups
relationship_dict = {}

def connect_db():
    """
    Connects to SQLite database (creates it if not exists).
    """
    conn = sqlite3.connect("relationships.db")
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            relationship TEXT UNIQUE,
            category TEXT
        )
    ''')
    conn.commit()
    return conn, cursor

def load_relationships():
    """
    Loads relationships from the database into the in-memory dictionary.
    """
    global relationship_dict
    conn, cursor = connect_db()
    cursor.execute("SELECT relationship, category FROM relationships")
    relationship_dict = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    print("✅ Relationships loaded into memory:", relationship_dict)

def get_relationship(relationship):
    """
    Retrieves the standardized category for a given relationship.
    """
    return relationship_dict.get(relationship, "unknown")

def add_relationship(relationship, category):
    """
    Adds a new relationship to both the database and dictionary.
    """
    global relationship_dict
    conn, cursor = connect_db()
    try:
        cursor.execute("INSERT INTO relationships (relationship, category) VALUES (?, ?)", (relationship, category))
        conn.commit()
        relationship_dict[relationship] = category  # ✅ Update memory
        print(f"✅ Added '{relationship}' as '{category}'")
    except sqlite3.IntegrityError:
        print(f"⚠️ Relationship '{relationship}' already exists!")
    finally:
        conn.close()

def update_relationship(relationship, new_category):
    """
    Updates an existing relationship in both the database and dictionary.
    """
    global relationship_dict
    conn, cursor = connect_db()
    cursor.execute("UPDATE relationships SET category = ? WHERE relationship = ?", (new_category, relationship))
    if cursor.rowcount:
        conn.commit()
        relationship_dict[relationship] = new_category  # ✅ Update memory
        print(f"✅ Updated '{relationship}' to '{new_category}'")
    else:
        print(f"⚠️ Relationship '{relationship}' not found!")
    conn.close()

def delete_relationship(relationship):
    """
    Deletes a relationship from both the database and dictionary.
    """
    global relationship_dict
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM relationships WHERE relationship = ?", (relationship,))
    if cursor.rowcount:
        conn.commit()
        relationship_dict.pop(relationship, None)  # ✅ Remove from memory
        print(f"✅ Deleted relationship '{relationship}'")
    else:
        print(f"⚠️ Relationship '{relationship}' not found!")
    conn.close()

# ✅ Step 2: Load relationships into memory on startup
load_relationships()

# ✅ Step 3: Test the functions
if __name__ == "__main__":
    add_relationship("wife", "spouse")
    add_relationship("brother", "sibling")
    update_relationship("brother", "family")
    delete_relationship("wife")
    print("🔍 Lookup 'brother':", get_relationship("brother"))
