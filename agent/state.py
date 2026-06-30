from typing import Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class State(TypedDict):
    """
    Graph state shared across all nodes.

    messages: Full conversation history with automatic message merging.
              Uses LangGraph's add_messages reducer — handles deduplication
              and proper ordering automatically.
    summary:  Compressed summary of older conversation history.
              Written by the summarize_node when message count exceeds threshold.
              Injected into the system prompt on each model call.
    """
    messages: Annotated[list[BaseMessage], add_messages]
    summary:  str
