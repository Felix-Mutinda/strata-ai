import typer
import strata_ai
from strata_ai_cli.commands.create_agent import create_agent

app = typer.Typer(
    name="strata",
    help="Strata AI CLI — Layered contracts for AI systems",
    add_completion=False,
)


@app.command("version")
def version_cmd():
    """Show CLI and SDK compatibility versions."""
    typer.echo("Strata CLI: 0.1.0")
    typer.echo(f"Strata SDK: {strata_ai.__version__}")
    typer.echo(
        f"Compatibility: SDK >={strata_ai.__version__}, <{int(strata_ai.__version__.split('.')[0]) + 1}.0.0"
    )


app.command("create-agent")(create_agent)

if __name__ == "__main__":
    app()
