# Architecture Decision Record

This document records the key architectural decisions in this system, the alternatives considered, and the rationale for each choice. It is intended to help engineers understand not just what the system does, but why it is built this way.

---

## 1. LangGraph StateGraph over Custom Orchestration

**Decision**: Use LangGraph's `StateGraph` as the agent orchestration layer rather than a custom loop.

**Context**: The most common pattern in production AI agents is a hand-rolled while-loop: call the LLM, check for tool calls, execute them, repeat. This works at small scale but becomes fragile as requirements grow.

**Rationale**: `StateGraph` provides several properties that are difficult to implement correctly by hand: (1) a typed, immutable state object that is passed between nodes rather than mutated in place; (2) a `checkpointer` interface that persists state automatically after each node execution, enabling resumable conversations; (3) `astream_events()`, which exposes fine-grained execution events without the application needing to instrument each step manually. The graph is compiled once at startup and reused across all requests, paying the compilation cost only once.

---

## 2. Async Nodes Throughout

**Decision**: All nodes (`model_node`, `tool_node`, `summarize_node`) are defined as `async def`.

**Context**: LangGraph supports both sync and async nodes. Sync nodes are simpler to write.

**Rationale**: Production servers handle concurrent requests. A sync node blocks the event loop for the duration of its I/O — typically 1–10 seconds per LLM call. With 10 concurrent users, a sync model node would serialize all requests. Async nodes allow the event loop to service other requests during I/O waits. Additionally, MCP tools are inherently async (they make HTTP requests); calling them from a sync node would require `asyncio.run()` inside a thread pool worker, which introduces a nested event loop problem. Making all nodes async avoids this class of issue entirely.

---

## 3. Pluggable Checkpointer with Graceful Fallback

**Decision**: The `get_checkpointer()` factory attempts the configured backend and falls back to `MemorySaver` on failure, logging a warning rather than crashing.

**Context**: Production systems sometimes start with degraded dependencies. A MongoDB cluster may be temporarily unreachable at startup.

**Rationale**: A crash-on-startup behavior for a missing database means any infrastructure hiccup takes down the agent entirely. The fallback policy keeps the agent running with in-memory state — conversations are not persisted, but new requests can still be served. This aligns with the principle that partial functionality is better than total unavailability. The warning log ensures the degraded state is observable.

---

## 4. Message Sanitization Before LLM Calls

**Decision**: `_safe_messages()` filters and truncates the message history before it is sent to the LLM.

**Context**: The LangGraph `add_messages` reducer accumulates all messages faithfully. In production, several conditions produce invalid message sequences: a tool execution that was interrupted mid-flight leaves an `AIMessage` with `tool_calls` but no corresponding `ToolMessage`; after summarization, the remaining messages may start with a `ToolMessage` (which has no `HumanMessage` anchor); tool results from external APIs can be arbitrarily large.

**Rationale**: Most LLM API providers return a 400 error or silent hallucination when they receive these invalid sequences. The sanitization layer makes the invalid-input behavior explicit and recoverable rather than dependent on provider-specific error handling. The 15,000-character truncation limit for tool results is calibrated to stay well within typical context windows while preserving meaningful content.

---

## 5. Event-Driven Streaming with Layer Separation

**Decision**: `stream_graph()` yields plain Python dicts; `api/sse.py` serializes them to SSE wire format; `ChatService` coordinates the two.

**Context**: It is common to inline SSE serialization directly into the streaming function.

**Rationale**: The separation has two practical benefits. First, `stream_graph()` can be tested independently without an HTTP layer — tests can call it directly and assert on the dict output. Second, the SSE format (the `data: ...\n\n` framing) is an output concern, not a business logic concern. The `__keepalive__` sentinel dict is the only protocol between the layers, and it is intentionally simple.

---

## 6. Rolling Conversation Summarization

**Decision**: When message count exceeds `SUMMARIZE_AFTER`, the `summarize_node` compresses old messages into a text summary, removes them from state, and injects the summary into the system prompt on subsequent calls.

**Context**: Naive implementations keep the full conversation in the message list indefinitely. At 10 messages per minute in a 30-minute session, this produces 300 messages — 50,000+ tokens — passed to the LLM on every subsequent request.

**Rationale**: The rolling summary approach keeps the active context window bounded and predictable regardless of conversation length. The summary is stored as a plain string in state (not messages), preventing it from being accidentally included in tool-call sequences. The `_text_only_messages()` helper strips `ToolMessage` entries before summarization because they contain raw API output that is not meaningful without the corresponding tool call context.

---

## 7. Provider-Agnostic LLM Factory

**Decision**: All LLM instantiation goes through `make_llm()`, which reads `OPENAI_BASE_URL` and constructs a `ChatOpenAI` instance. No provider-specific SDK is used anywhere else in the codebase.

**Context**: Enterprise AI deployments commonly require the ability to switch providers without redeployment — for cost, capability, or data residency reasons.

**Rationale**: `ChatOpenAI` with a custom `base_url` is compatible with any provider that implements the OpenAI REST API format, which has become the de facto standard interface for LLM APIs. The HTTP clients (`httpx.Client` and `httpx.AsyncClient`) are cached globally to reuse the underlying TCP connection pool across requests, reducing per-request connection overhead without sacrificing token freshness.
