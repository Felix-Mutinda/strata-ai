import os
from pathlib import Path
from typer.testing import CliRunner
import strata_ai
from strata_ai_cli.main import app

runner = CliRunner()


class TestCreateAgentCommand:
    def setup_method(self):
        self.original_cwd = os.getcwd()

    def teardown_method(self):
        os.chdir(self.original_cwd)

    def _run(self, tmp_path, *args):
        os.chdir(tmp_path)
        result = runner.invoke(app, list(args), catch_exceptions=False)
        assert result.exit_code == 0, f"CLI failed: {result.output}"
        return result

    def test_creates_directory_and_exits_zero(self, tmp_path):
        self._run(tmp_path, "create-agent", "my-test-agent")
        assert Path("my-test-agent").exists()

    def test_generates_expected_project_structure(self, tmp_path):
        self._run(tmp_path, "create-agent", "struct-test")
        agent_dir = Path("struct-test")
        assert (agent_dir / "pyproject.toml").exists()
        assert (agent_dir / ".env.example").exists()
        assert (agent_dir / "app" / "main.py").exists()
        assert (agent_dir / "agent" / "agent.py").exists()
        assert (agent_dir / "agent" / "tools.py").exists()
        assert (agent_dir / "tests" / "test_agent.py").exists()

    def test_injects_sdk_version_and_project_name(self, tmp_path):
        self._run(tmp_path, "create-agent", "inject-test")
        content = (Path("inject-test") / "pyproject.toml").read_text(encoding="utf-8")
        assert strata_ai.__version__ in content
        assert "inject-test" in content

    def test_path_based_project_name_sanitization(self, tmp_path):
        project_arg = "workspace/my-test-agent"
        self._run(tmp_path, "create-agent", project_arg)

        assert Path(project_arg).exists()

        pyproject_content = (Path(project_arg) / "pyproject.toml").read_text(
            encoding="utf-8"
        )
        assert 'name = "my-test-agent"' in pyproject_content
        assert "workspace/" not in pyproject_content

        env_content = (Path(project_arg) / ".env.example").read_text(encoding="utf-8")
        assert "STRATA_AI_SERVICE_NAME=my-test-agent" in env_content

    def test_refuses_existing_directory(self, tmp_path):
        os.chdir(tmp_path)
        Path("existing-project").mkdir()
        result = runner.invoke(app, ["create-agent", "existing-project"])
        assert result.exit_code == 1, (
            f"Expected exit code 1, got {result.exit_code}. Output: {result.output}"
        )
        assert "already exists" in result.output.lower()
