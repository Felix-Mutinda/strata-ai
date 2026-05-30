# Strata AI Architecture
**Philosophy:** Layered contracts for AI systems. Enterprise governance by default. Domain teams get a working, observable scaffold on Day 1.

## 🧭 Core Principles
1. **Inversion of Framework Dependency** → Agent patterns import `strata_ai`, never `langgraph` or `google.adk`. The runtime is a pluggable implementation detail.
2. **Type Hints ARE the Contract** → Tool schemas, agent I/O, and state transitions derive automatically from Python annotations. No manual JSON schema.
3. **Observability & Security On By Default** → OTel spans, PII filtering, guardrails, audit trails, and RFC 9457 errors activate automatically. Opt-out, not opt-in.
4. **Testability by Design** → `AgentRuntime` is injected. Tests use `MockRuntime`. Zero LLM calls required to validate logic.
5. **Progressive Complexity** → Simple ReAct agent = ~30 lines. Power users access graph nodes/edges. CLI covers 80% of enterprise cases.

## 🏗️ 5-Layer Contract Cake
```
┌─────────────────────────────────────────────────────────┐
│ L5: CLI Scaffolds (strata-cli)                          │
│   create-agent | create-api | create-batch |            |
|   create-serving (spec-only)                            |
├─────────────────────────────────────────────────────────┤
│ L4: Agent Patterns                                      │
│   ReAct | HITL | Orchestrator | Plan-and-Execute        │
│   Reflection | Parallelizer | RAG                       │
├─────────────────────────────────────────────────────────┤
│ L3: Core Primitives & Contracts                         │
│   BaseAgent | Tool | AgentState | Memory | Message      │
│   TaskQueueAdapter | StateMigrationRegistry             │
├─────────────────────────────────────────────────────────┤
│ L2: Cross-Cutting Concerns                              │
│   Observability (OTel) | Security (PII/Guardrails)      │
│   Governance (Audit/Lineage) | Evals                    │
├─────────────────────────────────────────────────────────┤
│ L1: Runtime Adapter                                     │
│   AgentRuntime ABC → LangGraphAdapter → ADKAdapter      │
└─────────────────────────────────────────────────────────┘
```

## 🔁 `AgentRuntime` ABC Surface (Published Contract)
```python
class AgentRuntime(ABC):
    @abstractmethod
    async def compile(self, definition: AgentDefinition) -> Any: ...
    @abstractmethod
    async def run(self, compiled: Any, input: Dict, config: RunConfig) -> AgentResult: ...
    @abstractmethod
    def stream(self, compiled: Any, input: Dict, config: RunConfig) -> AsyncGenerator[AgentEvent, None]: ...
    @abstractmethod
    async def checkpoint(self, thread_id: str, state: AgentState) -> None: ...
    @abstractmethod
    async def resume(self, thread_id: str, human_input: Dict) -> AgentResult: ...
```
**Ownership Boundary:** `BaseAgent` owns tool dispatch, retry/backoff, guardrails, and iteration limits. `AgentRuntime` owns graph topology, state persistence, streaming yield, and checkpoint storage.

## 🛡️ State & Memory Contracts
| Contract | Ownership | Behavior |
|----------|-----------|----------|
| `AgentState` | Core | Pydantic-validated, versioned (`state_version`), canonical truth |
| `StateMigrationRegistry` | Core | Explicit `vN→vN+1` callables. Adapter invokes on `resume()` before validation |
| `MemoryAdapter.fork()` | Runtime/Agent | Copy-on-write namespace. **Merge-on-complete** for orchestrators. Discard on failure |
| `TaskQueueAdapter` | Platform | HITL pending state & async polling. `InMemoryTaskQueue` (dev) ↔ `RedisTaskQueue` (prod) |

## 🚨 Internal Exception Hierarchy
```
StrataBaseError
├── LLMProviderError (rate_limit, context_overflow, malformed_tool)
├── GuardrailViolationError (prompt_injection, topic_boundary, cost_exceeded)
├── CheckpointStateError (schema_mismatch, missing_thread, version_drift)
└── DataLeakError (PII detected in prompt/output)
```
All map to RFC 9457 `ProblemDetail` at the API edge. Domain teams catch typed exceptions, not `Exception`.

## 🗂️ Anti-Refactor Workspace Layout
```
strata-ai/
├── sdk/ → src/strata_ai/          ← Core contract + domain modules (agent/api/batch)
├── cli/ → src/strata_ai_cli/         ← Thin scaffolding orchestrator (Jinja2 + Typer)
└── tests/                         ← Parity, mock runtime, CI gates
```
- `strata_ai.core` owns lifecycle, DI, OTel, security, governance, errors, state migration. **Never duplicated.**
- CLI/SDK versioning enforced via `cli_sdk_lock.toml` (range constraint, CI compatibility check).

## 📅 Phase Roadmap
| Phase | Focus | Deliverables |
|-------|-------|--------------|
| **1.0** | Core App Contract | `StrataAIApp`, DI, RFC 9457, Loguru lifespan |
| **1.1** | Runtime Inversion | `AgentRuntime` ABC, `MockRuntime`, `BaseAgent`, parity tests |
| **1.2** | Agent Patterns & `@tool` | `ReActAgent`, schema gen, LangGraph boundary mapping |
| **1.3** | State Migration & Task Queue | `StateMigrationRegistry`, `TaskQueueAdapter` ABC, `MemoryAdapter` scoping |
| **1.4** | CLI `create-agent` | Jinja2 templates, adapter injection, dev/prod parity |
| **2** | API & Batch Unification | Shared lifecycle, `create-api`/`create-batch`, `PipelineRuntime` ABC |
| **3** | Advanced Governance & ADK | `ADKAdapter`, eval pipeline, multi-runtime parity, release |