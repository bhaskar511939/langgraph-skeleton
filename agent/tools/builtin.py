import json
from langchain_core.tools import tool


@tool
def search_knowledge_base(query: str, limit: int | None = None) -> str:
    """
    Search the knowledge base for relevant documents.
    Use for: technical how-to questions, documentation, best practices.
    Replace this with your real vector database search implementation.
    """
    # TODO: Replace with real RAG implementation
    # Example: return chroma_client.query(query, n_results=limit or 5)
    return json.dumps({
        "query":   query,
        "results": [
            {"title": "Getting Started", "snippet": f"Documentation for: {query}", "score": 0.95},
        ],
    })


@tool
def get_current_info(topic: str = "") -> str:
    """
    Get current information about a topic.
    Use for: factual questions, current status, general information.
    Replace with your real data source.
    """
    # TODO: Replace with real implementation
    return json.dumps({
        "topic": topic or "general",
        "info":  "Replace with real data source implementation.",
    })


ALL_TOOLS = [search_knowledge_base, get_current_info]
