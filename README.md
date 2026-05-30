# Strata AI
**Layered contracts for AI systems. Enterprise governance by default.**

> The production skeleton for AI agents. Type-safe contracts, swappable runtimes, and governance enabled by default. Structured like FastAPI, built for reasoning topology.

## 🚀 Quick Start
```bash
# Scaffold a production-ready agent in <60 seconds
uvx strata-ai create-agent my-risk-analyst --pattern react --model anthropic:claude-sonnet-4-6
cd my-risk-analyst
cp .env.example .env && uv sync
uv run dev  # hot-reload :8080, console OTel, mock AI adapters, RFC 9457 errors
uv run test # deterministic, zero LLM calls
```

## 📦 Workspace Structure
| Path | Purpose | Docs |
|------|---------|------|
| `sdk/` | `strata-ai`: Core primitives, runtime adapters, enterprise contracts | [sdk/README.md](sdk/README.md) |
| `cli/` | `strata-ai-cli`: Scaffolding orchestrator, Jinja2 templates, Typer commands | [cli/README.md](cli/README.md) |
| `tests/` | Unit/integration parity tests, mock runtimes, CI gates | `CONTRIBUTING.md` |
| `ARCHITECTURE.md` | 5-layer design, inversion principles, phase roadmap | [Architecture](ARCHITECTURE.md) |

## 🎯 Why Strata?
- **FastAPI Mental Model** → `lifespan` → DI → middleware → routers → RFC errors. Same structure, agent topology.
- **Runtime Inversion** → Swap LangGraph ↔ ADK ↔ Mock without refactoring patterns.
- **Enterprise Defaults On** → OTel, PII filtering, guardrails, audit trails, structured errors.
- **Day 1 Scaffolds** → Platform owns bootstrap. Domain teams ship business logic immediately.

## 🛠️ Status
| Phase | Scope | Status |
|-------|-------|--------|
| 1.0 | Core App Contract | 🟢 Complete |
| 1.1 | Runtime Inversion | 🟢 Complete |
| 1.2 | Agent Patterns & `@tool` | 🟢 Complete |
| **1.3** | **State Migration & Task Queue** | 🟡 In Progress |
| 1.4 | CLI `create-agent` | ⬜ Planned |
| 2 | API & Batch Unification | ⬜ Planned |
| 3 | Advanced Governance & ADK | ⬜ Planned |

## 📖 Next Steps
1. Review [Architecture](ARCHITECTURE.md)
2. Read [SDK Docs](sdk/README.md) & [CLI Docs](cli/README.md)
3. Follow [Contributing Guidelines](CONTRIBUTING.md)