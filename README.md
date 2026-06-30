# LangGraph Production Skeleton

A production-grade framework for deploying stateful, multi-turn AI agents at enterprise scale. This skeleton distills engineering patterns developed and proven in a Fortune 5 technology company's internal AI infrastructure, generalized for the broader developer community.

## Overview

Building LangGraph agents that work in a notebook or a weekend prototype is straightforward. Building them to serve hundreds of thousands of employees reliably — with multi-turn memory, real-time streaming, parallel tool execution, and zero-downtime deployments — requires a fundamentally different approach. This project provides that foundation.

The codebase addresses the gap between LangGraph's excellent documentation examples and the engineering rigor that production systems demand. It is not a tutorial; it is the architecture that runs.

The patterns in this project directly address that gap:

- **Stateful multi-turn agents** that maintain coherent conversation context across sessions, enabling knowledge workers to have extended, productive dialogues with AI systems rather than isolated one-shot queries
- **Pluggable external tool integration via MCP** (Model Context Protocol), allowing organizations to connect agents to their existing data infrastructure without rewriting the agent
- **Provider-agnostic LLM interface** that allows organizations to choose their AI provider based on data sovereignty, cost, and capability requirements rather than being locked to a single vendor's SDK patterns
- **Real-time streaming with proper SSE handling** that provides responsive user experiences even for complex multi-step reasoning tasks

These are not academic contributions. They are the engineering prerequisites for AI adoption at scale in the American enterprise, which is itself a national economic priority.

## Architecture Highlights

### Stateful Graph with Persistent Checkpointing

The agent is implemented as a LangGraph `StateGraph` with a pluggable checkpointer. In development, an in-memory `MemorySaver` requires no external dependencies. In production, a `MongoDBSaver` provides durable state that survives server restarts and supports horizontal scaling across multiple instances.

Each conversation is keyed by `thread_id`, allowing the same server to maintain independent, isolated context for thousands of simultaneous users.

### Automatic Conversation Summarization

A critical production concern that most examples omit: unbounded context growth. This system implements a rolling summarization node that triggers when conversation history exceeds a configurable threshold. Older messages are compressed into a summary that is injected into the system prompt, keeping inference costs bounded without losing conversational continuity.

### MCP Tool Integration

The agent uses the Model Context Protocol to load tools from external servers at startup. This architecture allows tool development teams to publish and update tools independently of agent deployments. The MCP client supports bearer token authentication and gracefully degrades when servers are unavailable.

### Provider-Agnostic LLM Layer

All LLM calls route through a single `make_llm()` factory that accepts any OpenAI-compatible endpoint via `OPENAI_BASE_URL`. This supports OpenAI, Azure OpenAI, Anthropic Claude (via proxy), Google Gemini (via proxy), and local models via Ollama. Switching providers requires changing two environment variables, not modifying application code.

### Production-Safe Message Sanitization

A `_safe_messages()` function addresses a class of errors that are common in production but absent from tutorials: orphaned `ToolMessage` entries, `AIMessage` records with tool calls that have no corresponding results, and oversized tool outputs that overflow context windows. These conditions arise naturally in real usage patterns and cause silent failures or API errors without explicit handling.

## Quick Start

```bash
git clone https://github.com/bhaskararaorebba/langgraph-skeleton
cd langgraph-skeleton
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set OPENAI_API_KEY
python server.py
```

Visit `http://localhost:8000/docs` for the interactive API.

## API

```
POST /api/v1/chat/ask
{
  "query":   "What can you help me with?",
  "user_id": "user-123",
  "model":   "gpt-4o"   // optional
}
```

Response: `text/event-stream` — each event is a JSON object with `{type, stage, message, timestamp}`.

## Project Structure

```
langgraph-skeleton/
├── agent/
│   ├── graph.py          # StateGraph definition and compilation
│   ├── state.py          # Shared TypedDict state
│   ├── llm.py            # Provider-agnostic LLM factory
│   ├── events.py         # Unified streaming event contract
│   ├── stream_events.py  # astream_events() processing pipeline
│   ├── checkpointers/    # Memory (default) and MongoDB backends
│   ├── nodes/            # model, tool, summarize, route nodes
│   └── tools/            # Built-in tools + MCP loader
├── api/
│   ├── app.py            # FastAPI application with lifespan
│   ├── sse.py            # SSE serialization
│   ├── routes/           # /ask and /health endpoints
│   ├── schemas/          # Pydantic request/response models
│   └── services/         # ChatService streaming orchestration
├── config/               # Settings from environment variables
├── prompts/              # Markdown system prompt (editable)
├── utils/                # Logging and input validation
└── tests/                # Integration tests
```

## Extending This Skeleton

- **Add a tool**: Define a function with `@tool` in `agent/tools/builtin.py`
- **Add an MCP server**: Add an entry to `agent/tools/mcp_config.py`
- **Switch LLM providers**: Set `OPENAI_BASE_URL` and `OPENAI_API_KEY` in `.env`
- **Use persistent memory**: Set `MEMORY_BACKEND=mongodb` and `MONGODB_URI`
- **Customize the agent**: Edit `prompts/system.md`

## License

MIT
