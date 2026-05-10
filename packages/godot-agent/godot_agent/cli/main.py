"""Godot Agent CLI commands."""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from godot_agent import __version__
from godot_agent.assets import AssetPipeline, ImageMeta, AudioMeta, ModelMeta
from godot_agent.config import load_config, save_config, GodotAgentConfig, GodotConfig
from godot_agent.gdd import GDDEngine
from godot_agent.harness import HarnessRunner
from godot_agent.inspector import ProjectInspector
from godot_agent.scene import SceneDocument
from godot_agent.planner import GamePlanner
from godot_agent.planner.executor import PhaseExecutor
from godot_agent.bridge.registry import register_godot_tools
from nanobot.agent.tools.registry import ToolRegistry

app = typer.Typer(
    name="godot-agent",
    help="AI-powered agent for Godot 4.x game development",
    no_args_is_help=True,
)
console = Console()


def _load_cfg(config: Optional[str] = None):
    """Load configuration with optional override."""
    return load_config(config)


@app.command()
def version():
    """Show version."""
    console.print(f"godot-agent [bold green]{__version__}[/bold green]")


@app.command()
def init(
    project: str = typer.Option(".", "--project", "-p", help="Godot project path"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
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

    # Create default config
    cfg = GodotAgentConfig(godot=GodotConfig(project_path=str(project_path)))
    saved = save_config(cfg, config)
    console.print(f"[green]Created config at[/green] {saved}")

    console.print(f"\n[bold]Project initialized at {project_path}[/bold]")


@app.command()
def config_show(
    config: Optional[str] = typer.Option(None, "--config", "-c"),
):
    """Show current configuration."""
    cfg = _load_cfg(config)
    console.print_json(data=cfg.model_dump(by_alias=True))


@app.command()
def inspect(
    project: str = typer.Option(".", "--project", "-p", help="Godot project path"),
):
    """Inspect a Godot project and print a report."""
    inspector = ProjectInspector(project)
    report = inspector.inspect()
    
    table = Table(title=f"Project Report: {report.project_name or 'Unnamed'}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Path", report.project_path)
    table.add_row("Godot Version", report.godot_version or "unknown")
    table.add_row("Scenes", str(report.stats.get("scene_count", 0)))
    table.add_row("Scripts", str(report.stats.get("script_count", 0)))
    table.add_row("Total Lines", str(report.stats.get("total_lines", 0)))
    table.add_row("Autoloads", str(report.stats.get("autoload_count", 0)))
    table.add_row("Input Actions", str(report.stats.get("input_action_count", 0)))
    table.add_row("Total Nodes", str(report.stats.get("nodes_total", 0)))
    
    console.print(table)
    
    if report.autoloads:
        console.print("\n[bold]Autoloads:[/bold]")
        for a in report.autoloads:
            singleton = " (singleton)" if a["singleton"] else ""
            console.print(f"  {a['name']} -> {a['path']}{singleton}")
    
    if report.scenes:
        console.print("\n[bold]Scenes:[/bold]")
        for s in report.scenes:
            console.print(f"  {s.path} — {s.node_count} nodes ({s.root_type})")
    
    if report.scripts:
        console.print("\n[bold]Scripts:[/bold]")
        for s in report.scripts:
            cls = f" [class: {s.class_name}]" if s.class_name else ""
            console.print(f"  {s.path} — {s.line_count} lines{cls}")
    
    if report.warnings:
        console.print("\n[bold red]Warnings:[/bold red]")
        for w in report.warnings:
            console.print(f"  ! {w}")


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
def generate(
    requirement: str = typer.Argument(..., help="Natural language game requirement"),
    project: str = typer.Option(".", "--project", "-p", help="Godot project path"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show plan without executing"),
):
    """Generate a complete Godot game from a natural language requirement."""
    from godot_agent.workflow.real_llm import get_llm_client

    llm = get_llm_client()
    planner = GamePlanner(llm)
    registry = ToolRegistry()
    register_godot_tools(registry)
    executor = PhaseExecutor(registry)

    async def run():
        console.print(f"[bold]Planning game: {requirement}[/bold]")
        try:
            plan = await planner.plan(requirement, project_root=project)
        except Exception as exc:
            console.print(f"[red]Planning failed: {exc}[/red]")
            raise typer.Exit(1)

        console.print(f"[green]Genre: {plan.genre}[/green]")
        console.print(f"[green]Phases: {len(plan.phases)}[/green]")

        for phase in plan.phases:
            console.print(f"  • {phase.name} ({phase.tool})")

        if dry_run:
            console.print("[yellow]Dry run — not executing phases[/yellow]")
            return

        console.print("\n[bold]Executing phases...[/bold]")
        results = await executor.execute_plan(plan)

        for result in results:
            status = "[green]✓[/green]" if result.success else "[red]✗[/red]"
            console.print(f"{status} {result.phase_id}")
            if result.errors:
                for err in result.errors:
                    console.print(f"    [red]{err}[/red]")

        success_count = sum(1 for r in results if r.success)
        console.print(f"\n[bold]{success_count}/{len(results)} phases completed[/bold]")

    asyncio.run(run())


@app.command()
def harness(
    test_script: Optional[str] = typer.Argument(None, help="Test script path"),
    project: str = typer.Option(".", "--project", "-p"),
    all_tests: bool = typer.Option(False, "--all", help="Run all tests"),
    godot_path: Optional[str] = typer.Option(None, "--godot"),
):
    """Run Godot test harness."""
    runner = HarnessRunner(project, godot_path=godot_path or "godot")

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
