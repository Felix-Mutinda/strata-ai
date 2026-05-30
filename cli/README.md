# Strata AI CLI
**Thin scaffolding orchestrator. Generates Day 1 production repos. Enforces platform/dev boundaries.**

## 📦 Installation
```bash
uvx strata-ai-cli  # no install required
# or pip install strata-ai-cli
```

## 🛠️ Commands
| Command | Purpose | Output |
|---------|---------|--------|
| `create-agent` | ReAct, HITL, Orchestrator, etc. | `agent/`, `evals/`, `deployment/`, `tests/`, pre-wired `app/main.py` |
| `create-api` | Generic FastAPI microservice | `services/`, `routers/`, `repositories/`, task polling |
| `create-batch` | Spark/Kubeflow/Airflow pipelines | `pipelines/`, `notebooks/`, `io/`, async queue hooks |
| `create-serving` | MLflow/Cloud Run/GKE model serving | `serving/`, `terraform/`, `cloudbuild.yaml`, auth specs |

## 📐 Template Contract
All commands share a **single base template**. Only `app/main.py` router inclusion and domain folder differ:
```bash
uvx strata-ai-cli create-agent my-agent
cd my-agent && uv run dev  # identical bootstrap for agent/api/batch
```

### Platform vs Developer Ownership
```
PLATFORM OWNS (dev no-touch)          DEV OWNS
app/core/lifespan.py                  app/schemas/
app/core/middleware.py                app/services/
app/core/exceptions.py                app/routers/
app/core/dependencies.py              app/repositories/
app/routers/agent.py (pre-generated)  agent/agent.py
                                      agent/tools.py
                                      agent/config.py
                                      agent/prompts/
```

## 🔄 Adding Commands
Follow the 4-step pattern in `CONTRIBUTING.md`. No changes to existing commands required. Jinja2 templates receive standard context (`project_name`, `sdk_version`, etc.).

## 🚦 Day 1 Workflow
1. `uvx strata-ai-cli create-<type> <name>`
2. `cp .env.example .env && uv sync`
3. `uv run dev` → hot-reload :8080, console OTel, mock adapters, RFC 9457 errors
4. `uv run test` → deterministic, `MockRuntime` injected, ≥80% coverage enforced
