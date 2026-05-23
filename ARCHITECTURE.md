# Strata AI Architecture
**Philosophy:** *Layered contracts for AI systems. Enterprise governance by default. Domain teams get a working, observable scaffold on Day 1.*

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
│   create-agent | create-api | create-batch              |
├─────────────────────────────────────────────────────────┤
│ L4: Agent Patterns                                      │
│   ReAct | HITL | Orchestrator | Plan-and-Execute        │
│   Reflection | Parallelizer | RAG                       │
├─────────────────────────────────────────────────────────┤
│ L3: Core Primitives                                     │
│   BaseAgent | Tool | AgentState | Memory | Message      │
├─────────────────────────────────────────────────────────┤
│ L2: Cross-Cutting Concerns                              │
│   Observability (OTel) | Security (PII/Guardrails)      │
│   Governance (Audit/Lineage) | Evals                    │
├─────────────────────────────────────────────────────────┤
│ L1: Runtime Adapter                                     │
│   AgentRuntime ABC → LangGraphAdapter → ADKAdapter      │
└─────────────────────────────────────────────────────────┘
```

## 🔁 Inversion of Control
The `AgentRuntime` ABC isolates framework coupling:
```python
# Pattern code NEVER imports langgraph/adk
from strata_ai import ReActAgent, AgentConfig
from strata_ai.runtime import LangGraphAdapter  # swappable

agent = ReActAgent(config=..., runtime=LangGraphAdapter())
# Swap to ADKAdapter() or MockRuntime() without touching agent logic
```

## 🛡️ Enterprise Defaults
| Concern | Implementation | Production Guarantee |
|---------|----------------|----------------------|
| Observability | OTel auto-instrumentation → MLflow/Langfuse/OTLP | Trace trees, token/cost tracking, latency percentiles |
| Security | `PIIFilter` (MSISDN, ID, email, refs) + `Guardrail` middleware | Prompt injection detection, topic boundaries, cost hard-stops |
| Governance | `AuditLog` (immutable) + `LineageTracker` (MLflow-backed) | Run-to-model/version/prompt mapping. GDPR-compliant sinks |
| Errors | RFC 9457 `ProblemDetail` handlers | Standardized frontend/CLI parity. Zero 500 leaks |

## 🗂️ Anti-Refactor Workspace Layout
```
strata-ai/
├── sdk/ → src/strata_ai/          ← Core contract + domain modules (agent/api/batch)
├── cli/ → src/strata_cli/      ← Thin scaffolding orchestrator (Jinja2 + Typer)
└── tests/                      ← Parity, mock runtime, CI gates
```
- `strata_ai.core` owns lifecycle, DI, OTel, security, governance, errors. **Never duplicated.**
- `strata_ai.agent`, `strata_ai.api`, `strata_ai.batch` are **thin domain layers** consuming `core` contracts.
- CLI generates **identical repo skeletons**; only `app/main.py` router inclusion differs.

## 🤝 Integration Philosophy
- **We scaffold contracts, not runtimes.** Generate code that integrates with LangGraph, ADK, Langfuse, MLflow, Prefect. Do not replace them.
- **FastAPI mental model:** `StrataAIApp.build()` → lifespan → DI → middleware → routers → RFC errors. Same structure, agent topology.
- **Day 1 scaffolds:** Platform owns bootstrap. Domain teams own business logic. Clear ownership boundaries prevent refactor debt.

## 📅 Phase Roadmap
| Phase | Focus | Deliverables |
|-------|-------|--------------|
| 0 | Foundation & Contract | `AgentRuntime` ABC, `MockRuntime`, `StrataAIApp.build()`, workspace setup, semantic-release |
| 1 | Core & Agent MVP | `strata_ai.core`, `ReActAgent`, `@tool`, `LangGraphAdapter`, `create-agent` CLI, OTel bootstrap |
| 2 | API & Batch Unification | `strata_ai.api`, `strata_ai.batch`, `create-api`, `create-batch`, shared lifecycle parity |
| 3 | Enterprise Defaults | PII, guardrails, `AuditLog`, `HITLAgent`, `AgentEvaluator`, `create-serving` |
| 4 | Release & Docs | PyPI publish, migration guides, CI/CD fallback, contributor automation |