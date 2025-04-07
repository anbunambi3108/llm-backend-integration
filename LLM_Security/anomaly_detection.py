import time

query_attempts = {}

def detect_anomaly(user_id):
    """
    Flags suspicious query activity (e.g., too many requests in a short time).
    """
    now = time.time()

    if user_id not in query_attempts:
        query_attempts[user_id] = []

    query_attempts[user_id].append(now)

    # If user makes more than 5 requests in 10 seconds, flag them
    if len(query_attempts[user_id]) > 5:
        return f"🚨 ALERT: Possible data scraping attempt by user {user_id}!"
    
    return "Normal activity."
