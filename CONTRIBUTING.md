# Contributing to Strata AI
Strict contracts. Clear boundaries. Testability first.

## 📦 Adding a New SDK Module (e.g., `strata_ai.catalog`)
1. Create `sdk/src/sdk/<module>/`
   ```
   ├── __init__.py      (clean public surface, defines __all__)
   ├── core.py          (implementation)
   └── tests/test_core.py (co-located or in tests/sdk/)
   ```
2. Export from `sdk/src/sdk/__init__.py` if top-level. Submodule import preferred: `from strata_ai.catalog import ...`
3. Add tests to `tests/sdk/test_<module>.py` (≥80% coverage, `pytest-asyncio` where applicable)
4. Commit with conventional format:
   ```
   feat(catalog): add UseCaseRegistry and AgentRegistry   → minor bump (0.x.0)
   fix(catalog): handle missing GCP_PROJECT_ID gracefully  → patch bump (0.0.x)
   ```

### 📐 Module Interface Contract
Every SDK module must:
- Define config via `StrataAIBaseConfig` fields (no hardcoded secrets/mandatory defaults)
- Provide a `from_env()` classmethod or constructor reading from settings
- Declare `__all__` in `__init__.py`
- Achieve ≥80% test coverage
- **Never import from `cli`** (CLI depends on SDK, not reverse)

## 🛠️ Adding a New CLI Scaffold Command (e.g., `create-batch`)
1. Create `cli/src/cli/commands/create_<name>.py` (copy `create_agent.py` as baseline)
2. Create `cli/src/cli/templates/<name>/` (Jinja2 `.j2` files; supports dynamic filenames/content)
3. Register in `cli/src/cli/main.py`:
   ```python
   from cli.commands.create_batch import create_batch
   app.command("create-batch")(create_batch)
   ```
4. Add tests to `tests/cli/test_scaffold.py`:
   ```python
   class TestCreateBatchCommand:
       def test_creates_directory(self, tmp_path): ...
       def test_generates_key_files(self, tmp_path): ...
   ```
5. Commit: `feat(cli): add create-batch command for Airflow and Kubeflow DAGs → cli minor bump`

### 📐 Template Variable Contract
| Key | Value | Example |
|-----|-------|---------|
| `project_name` | CLI argument | `my-churn-pipeline` |
| `project_name_title` | Title-cased | `My Churn Pipeline` |
| `sdk_version` | Current SDK version | `0.1.0` |
| Command-specific keys | Defined in command file | Documented in template `README.md.j2` |

## 🔄 Semver Commit Cheat Sheet
| Prefix | Bump | Example |
|--------|------|---------|
| `feat:` | minor | `feat(agent): add ReflectionAgent pattern → 0.1.0 → 0.2.0` |
| `fix:` / `perf:` / `refactor:` | patch | `fix(core): handle missing OTLP endpoint gracefully → 0.1.0 → 0.1.1` |
| `docs:` / `chore:` / `ci:` / `test:` | none | `docs: add HITL pattern example to README` |
| `feat!:` or `BREAKING CHANGE:` | major | `feat!: remove LangGraphAdapter.sync_compile() → 0.1.0 → 1.0.0` |

## 🔄 CLI/SDK Versioning
- `cli_sdk_lock.toml` enforces range compatibility: `sdk >= 0.x.0, < 0.(x+1).0`
- `feat(cli)` consuming new SDK features **must** be preceded by `feat(sdk)` minor bump.
- CI runs `uvx strata verify-compatibility` to validate generated `pyproject.toml` against lock.

## 🚦 Release Checklist (Automated via CI, manual fallback)
1. Merge PR to `main` (all CI checks green: `ruff`, `pyright`, `pytest`, coverage ≥80%)
2. Run manually if needed:
   ```bash
   uv run semantic-release version    # bumps version + updates CHANGELOG.md
   git push --follow-tags             # pushes commit + tag
   cd sdk && hatch build              # builds wheel
   cd cli && hatch build
   uv publish --index-url <internal-pypi> */dist/*.whl
   ```

## 🛡️ Ownership Boundaries (Enforced by CLI + Linting)
| Layer | Owner | Rules |
|-------|-------|-------|
| `app/core/` | Platform | Never modified by domain teams. Contains lifespan, DI, OTel, middleware, RFC errors |
| `app/routers/agent.py` | Platform (generated) | Pre-wired to domain `agent/agent.py`. No middleware changes required |
| `agent/`, `services/`, `pipelines/` | Domain Teams | Own business logic, tools, schemas, repos, prompts |
| `tests/` | Shared | Domain tests mock infrastructure. Platform tests verify lifecycle parity & contract enforcement |