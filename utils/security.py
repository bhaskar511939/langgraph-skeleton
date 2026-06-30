MAX_QUERY_LENGTH = 4000


def validate_query(query: str) -> str:
    """Validate and sanitize user input at the API boundary."""
    query = query.strip()
    if not query:
        raise ValueError("Query cannot be empty")
    if len(query) > MAX_QUERY_LENGTH:
        raise ValueError(f"Query too long (max {MAX_QUERY_LENGTH} characters)")
    return query
