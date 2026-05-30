# cli/src/strata_cli/commands/create_agent.py
from pathlib import Path
import typer
import jinja2
from rich.console import Console
import strata_ai

console = Console()


def create_agent(
    project_name: str = typer.Argument(
        ..., help="Name or relative path of the project to scaffold"
    ),
    pattern: str = typer.Option(
        "react", help="Agent pattern: react, hitl, orchestrator"
    ),
    model: str = typer.Option("openai:gpt-4o", help="Default LLM model identifier"),
):
    """Scaffold a production-ready Strata AI agent project with enterprise defaults."""
    out_dir = Path(project_name)
    # Extract sanitized name for package/config usage
    raw_project_name = out_dir.name

    if not raw_project_name or raw_project_name in (".", ".."):
        console.print(
            "[red]Error:[/red] Invalid project name. Provide a valid directory path."
        )
        raise typer.Exit(1)

    if out_dir.exists():
        console.print(f"[red]Error:[/red] Directory '{project_name}' already exists.")
        raise typer.Exit(1)

    template_dir = Path(__file__).parent.parent / "templates" / "base"
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )

    context = {
        "project_name": raw_project_name,
        "project_name_title": raw_project_name.replace("-", " ").title(),
        "sdk_version": strata_ai.__version__,
        "pattern": pattern,
        "model": model,
    }

    console.print(f"[bold blue]Scaffolding agent:[/bold blue] {project_name}")
    out_dir.mkdir(parents=True, exist_ok=False)  # Support nested paths

    for template_path in template_dir.rglob("*.j2"):
        relative = template_path.relative_to(template_dir)
        template_key = relative.as_posix()  # Cross-platform Jinja2 compatibility

        # Handle dynamic filenames (e.g., {{ project_name }}.py.j2)
        raw_name = relative.name
        if raw_name.endswith(".j2"):
            target_name = jinja2.Template(raw_name[:-3]).render(context)
        else:
            target_name = raw_name

        target_path = out_dir / relative.parent / target_name
        target_path.parent.mkdir(parents=True, exist_ok=True)

        template = env.get_template(template_key)
        content = template.render(context)
        target_path.write_text(content, encoding="utf-8")
        console.print(f"  [green]Created:[/green] {target_path.relative_to(out_dir)}")

    # Generate CLI/SDK lock for compatibility tracking
    lock_content = f"""[compatibility]
cli_version = "{strata_ai.__version__}"
sdk_range = ">={strata_ai.__version__}, <{int(strata_ai.__version__.split(".")[0]) + 1}.0.0"
generated_for = "{raw_project_name}"
"""
    (out_dir / "cli_sdk_lock.toml").write_text(lock_content, encoding="utf-8")
    console.print("  [green]Created:[/green] cli_sdk_lock.toml")

    console.print("\n[bold green]✅ Agent scaffolded successfully![/bold green]")
    console.print(f"[dim]cd {project_name} && cp .env.example .env && uv run dev[/dim]")
