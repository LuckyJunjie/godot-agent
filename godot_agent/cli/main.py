"""Godot Agent CLI commands."""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from godot_agent import __version__
from godot_agent.assets import AssetPipeline, ImageMeta, AudioMeta, ModelMeta
from godot_agent.gdd import GDDEngine
from godot_agent.harness import HarnessRunner
from godot_agent.scene import SceneDocument

app = typer.Typer(
    name="godot-agent",
    help="AI-powered agent for Godot 4.x game development",
    no_args_is_help=True,
)
console = Console()


@app.command()
def version():
    """Show version."""
    console.print(f"godot-agent [bold green]{__version__}[/bold green]")


@app.command()
def init(
    project: str = typer.Option(".", "--project", "-p", help="Godot project path"),
):
    """Initialize a Godot project with agent scaffolding."""
    project_path = Path(project).resolve()
    project_path.mkdir(parents=True, exist_ok=True)

    # Initialize GDD
    gdd = GDDEngine(str(project_path))
    gdd.initialize()
    console.print(f"[green]Initialized GDD at[/green] {gdd.gdd_dir}")

    # Initialize asset pipeline
    assets = AssetPipeline(str(project_path))
    assets.initialize()
    console.print(f"[green]Initialized assets at[/green] {assets.output_dir}")

    # Create test directory
    test_dir = project_path / "tests"
    test_dir.mkdir(exist_ok=True)
    (test_dir / "__init__.py").touch()
    console.print(f"[green]Initialized tests at[/green] {test_dir}")

    console.print(f"\n[bold]Project initialized at {project_path}[/bold]")


@app.command()
def scene_inspect(
    path: str = typer.Argument(..., help="Path to .tscn file"),
):
    """Inspect a Godot scene file."""
    doc = SceneDocument()
    doc.load(path)
    console.print(f"[bold]Scene:[/bold] {path}")
    console.print(f"External resources: {len(doc.ext_resources)}")


@app.command()
def gdd_validate(
    project: str = typer.Option(".", "--project", "-p"),
    strict: bool = typer.Option(False, "--strict"),
):
    """Validate GDD traceability."""
    engine = GDDEngine(project)
    result = engine.validate_traceability()

    if result["valid"]:
        console.print("[bold green]GDD is valid[/bold green]")
    else:
        console.print("[bold red]GDD issues found:[/bold red]")
        for issue in result["issues"]:
            console.print(f"  - {issue}")
        if strict:
            raise typer.Exit(1)


@app.command()
def harness(
    test_script: Optional[str] = typer.Argument(None, help="Test script path"),
    project: str = typer.Option(".", "--project", "-p"),
    all_tests: bool = typer.Option(False, "--all", help="Run all tests"),
):
    """Run Godot test harness."""
    runner = HarnessRunner(project)

    async def run():
        if test_script:
            result = await runner.run_unit(test_script)
            console.print(f"[{'green' if result.passed else 'red'}]{result.message}[/{'green' if result.passed else 'red'}]")
        elif all_tests:
            # TODO: discover and run all tests
            console.print("[yellow]All-test discovery not yet implemented[/yellow]")
        else:
            console.print("[yellow]Specify a test script or --all[/yellow]")

    asyncio.run(run())


# Asset CLI subcommands
asset_app = typer.Typer(help="Asset generation commands")
app.add_typer(asset_app, name="asset")


@asset_app.command("generate")
def asset_generate(
    asset_type: str = typer.Argument(..., help="image | audio | model"),
    prompt: str = typer.Option(..., "--prompt", "-p"),
    name: str = typer.Option(..., "--name", "-n"),
    project: str = typer.Option(".", "--project"),
    model: Optional[str] = typer.Option(None, "--model"),
    resolution: Optional[str] = typer.Option(None, "--resolution"),
    duration: Optional[float] = typer.Option(None, "--duration"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Generate a game asset via LLM API."""
    pipeline = AssetPipeline(project)
    pipeline.initialize()

    async def run():
        if dry_run:
            console.print(f"[yellow]Dry run: would generate {asset_type} '{name}'[/yellow]")
            console.print(f"Prompt: {prompt}")
            return

        if asset_type == "image":
            w, h = 256, 256
            if resolution:
                w, h = map(int, resolution.split("x"))
            meta = ImageMeta(prompt=prompt, model=model or "dall-e-3", resolution=(w, h))
            path = await pipeline.generate_image(meta, name)
            console.print(f"[green]Generated image:[/green] {path}")
        elif asset_type == "audio":
            meta = AudioMeta(prompt=prompt, model=model or "elevenlabs", duration=int(duration or 3))
            path = await pipeline.generate_audio(meta, name)
            console.print(f"[green]Generated audio:[/green] {path}")
        elif asset_type == "model":
            meta = ModelMeta(prompt=prompt, model=model or "trellis")
            path = await pipeline.generate_model(meta, name)
            console.print(f"[green]Generated model:[/green] {path}")
        else:
            console.print(f"[red]Unknown asset type: {asset_type}[/red]")

    asyncio.run(run())


@asset_app.command("list")
def asset_list(
    project: str = typer.Option(".", "--project"),
    asset_type: Optional[str] = typer.Option(None, "--type"),
):
    """List generated assets."""
    pipeline = AssetPipeline(project)
    assets = pipeline.list_assets(asset_type)

    table = Table(title="Generated Assets")
    table.add_column("Path", style="cyan")
    table.add_column("Type", style="magenta")

    for a in assets:
        table.add_row(str(a), a.suffix.lstrip("."))

    console.print(table)


if __name__ == "__main__":
    app()
