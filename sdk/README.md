# Strata AI SDK
**Core contract layer for AI agents. Runtime-agnostic. Enterprise-ready by default.**

## 📦 Installation
```bash
uv add strata-ai
```

## 🧩 Module Structure
| Package | Purpose |
|---------|---------|
| `strata_ai.core` | `StrataAIApp.build()`, lifespan, DI, OTel, security, governance, RFC 9457, `StateMigrationRegistry`, `TaskQueueAdapter` |
| `strata_ai.agent` | `BaseAgent`, `ReActAgent`, `HITLAgent`, `OrchestratorAgent`, `@tool`, `AgentState`, `MemoryAdapter` |
| `strata_ai.api` | FastAPI middleware stack, task routers, sync/async polling contracts |
| `strata_ai.batch` | `BasePipeline`, async queue adapters, feature store IO, eval golden runners |
| `strata_ai.runtime` | `AgentRuntime` ABC, `LangGraphAdapter`, `MockRuntime` (strict mode), checkpoint/resume |

## 🔁 Runtime Inversion
Agent patterns **never** import framework internals. The runtime is injected:
```python
from strata_ai import ReActAgent, AgentConfig
from strata_ai.runtime import LangGraphAdapter

agent = ReActAgent(
    config=AgentConfig(name="analyst", model="openai:gpt-4o", instructions="..."),
    runtime=LangGraphAdapter(checkpointer=postgres),
    tools=[sql_query, web_search]
)
result = await agent.run({"question": "What is the GDP of Kenya?"})
```
Swap runtimes in config. Zero pattern refactors.

## 🛡️ Enterprise Defaults
- **Observability:** OTel spans auto-emitted on every `run()`, `stream()`, `tool.call`. Ships to MLflow/Langfuse/OTLP.
- **Security:** `PIIFilter` (MSISDN, ID, email, refs) + `Guardrail` middleware. Enabled when `pii_sensitive=True`.
- **Governance:** `AuditLog` (immutable) + `LineageTracker` (MLflow-backed). GDPR-compliant sink adapters.
- **Errors:** `StrataBaseError` hierarchy → RFC 9457 `ProblemDetail` at API edge. Zero 500 leaks.

## 🧪 Testability
```python
from strata_ai.runtime import MockRuntime

# Strict mode enforces 5 invariants: state immutability, tool-result pairing, checkpoint-before-resume, audit-on-violation, deterministic threads
agent = ReActAgent(config=..., runtime=MockRuntime(strict=True), tools=[...])
result = await agent.run({"input": "test"})
```
Zero LLM calls. Fast CI. Pattern parity verified via `tests/integration/test_runtime_parity.py`.