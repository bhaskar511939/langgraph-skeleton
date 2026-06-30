import json


def sse(event_dict: dict) -> str:
    """Serialize an event dict to SSE wire format."""
    return f"data: {json.dumps(event_dict)}\n\n"


def keepalive() -> str:
    """SSE comment line — keeps connection alive during long tool calls."""
    return ":\n\n"
