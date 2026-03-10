"""Rich-powered interactive prompts for the ClipDigest CLI."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich import box

from clipdigest.config import (
    Config,
    ModelConfig,
    SUPPORTED_PROVIDERS,
    DEFAULT_MODELS,
    ENV_KEYS,
    SYSTEM_PROMPT,
)

console = Console()


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _ask(prompt: str, default: str | None = None, password: bool = False) -> str:
    return Prompt.ask(prompt, default=default, password=password, console=console)


def _confirm(prompt: str, default: bool = True) -> bool:
    return Confirm.ask(prompt, default=default, console=console)


def _print_setting(label: str, value: str, source: str = "") -> None:
    suffix = f" [dim]({source})[/dim]" if source else ""
    console.print(f"  [cyan]{label}:[/cyan] [bold]{value}[/bold]{suffix}")


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------

def collect_urls() -> list[str]:
    """Ask the user for one or more YouTube URLs."""
    console.print(Panel("[bold]Step 1 of 4 — Video URLs[/bold]", style="blue"))

    urls: list[str] = []
    while True:
        raw = _ask("Enter a YouTube URL (leave blank to finish)" if urls else "Enter a YouTube URL")
        if not raw:
            if not urls:
                console.print("[red]Please enter at least one URL.[/red]")
                continue
            break
        urls.append(raw.strip())
        console.print(f"  [green]✓[/green] Added ({len(urls)} total)")

    return urls


def collect_model_config() -> ModelConfig:
    """Interactively choose provider, model, and API key."""
    console.print(Panel("[bold]Step 2 of 4 — Language Model[/bold]", style="blue"))

    # --- provider ---
    console.print("Supported providers:")
    for i, p in enumerate(SUPPORTED_PROVIDERS, 1):
        console.print(f"  [dim]{i}.[/dim] {p}")

    provider_input = _ask(
        "Provider name or number", default="openai"
    )
    # allow numeric shortcut
    if provider_input.isdigit():
        idx = int(provider_input) - 1
        if 0 <= idx < len(SUPPORTED_PROVIDERS):
            provider = SUPPORTED_PROVIDERS[idx]
        else:
            console.print("[yellow]Invalid number, defaulting to openai.[/yellow]")
            provider = "openai"
    elif provider_input in SUPPORTED_PROVIDERS:
        provider = provider_input
    else:
        console.print(f"[yellow]Unknown provider {provider_input!r}, defaulting to openai.[/yellow]")
        provider = "openai"

    # --- model ---
    default_model = DEFAULT_MODELS.get(provider, "")
    model = _ask("Model name", default=default_model)

    # --- API key ---
    env_key_name = ENV_KEYS.get(provider)
    api_key: Optional[str] = None

    if env_key_name:
        env_value = os.environ.get(env_key_name, "")
        if env_value:
            console.print(
                f"\n  [green]Found[/green] [bold]{env_key_name}[/bold] in environment "
                f"([dim]{env_value[:6]}…{env_value[-4:]}[/dim])"
            )
            use_env = _confirm(f"  Use the key already set in {env_key_name}?", default=True)
            if use_env:
                api_key = env_value
            else:
                api_key = _ask(f"  Enter your {env_key_name}", password=True)
        else:
            console.print(f"\n  [yellow]{env_key_name}[/yellow] is not set in the environment.")
            api_key = _ask(f"  Enter your {env_key_name}", password=True)
    else:
        console.print(f"\n  [dim]Provider {provider!r} does not require an API key.[/dim]")

    return ModelConfig(provider=provider, model=model, api_key=api_key or None)


def collect_prompt_config() -> str:
    """Ask the user whether to use the default prompt or supply a custom one."""
    console.print(Panel("[bold]Step 3 of 4 — System Prompt[/bold]", style="blue"))

    use_default = _confirm("Use the built-in summarization prompt?", default=True)
    if use_default:
        return SYSTEM_PROMPT

    console.print("Options: [1] type/paste now  [2] load from file")
    choice = _ask("Choice", default="1")
    if choice == "2":
        path_str = _ask("Path to prompt file")
        path = Path(path_str).expanduser()
        if path.exists():
            return path.read_text(encoding="utf-8")
        else:
            console.print("[red]File not found; falling back to built-in prompt.[/red]")
            return SYSTEM_PROMPT
    else:
        console.print("Paste/type your prompt. Enter a line with just [bold]END[/bold] when done:")
        lines: list[str] = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        return "\n".join(lines) or SYSTEM_PROMPT


def collect_output_config() -> tuple[str, bool, bool]:
    """Ask where to save outputs and which artefacts to keep.

    Returns:
        Tuple of (output_dir, save_transcript_json, save_transcript_txt).
    """
    console.print(Panel("[bold]Step 4 of 4 — Output Settings[/bold]", style="blue"))

    output_dir = _ask("Output directory", default="outputs")
    save_json = _confirm("Save raw transcript as JSON?", default=True)
    save_txt = _confirm("Save plain-text transcript?", default=True)
    return output_dir, save_json, save_txt


# ---------------------------------------------------------------------------
# Summary display
# ---------------------------------------------------------------------------

def show_config_summary(config: Config) -> None:
    """Print a summary table of the resolved configuration."""
    mc = config.model_config
    table = Table(title="Configuration Summary", box=box.ROUNDED, show_header=False)
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="bold")

    table.add_row("URLs", str(len(config.urls)))
    for i, url in enumerate(config.urls, 1):
        table.add_row(f"  [{i}]", url)
    table.add_row("Provider", mc.provider if mc else "—")
    table.add_row("Model", mc.model if mc else "—")
    table.add_row("API Key", "set" if (mc and mc.api_key) else "not set / not needed")
    table.add_row("Output dir", config.output_dir)
    table.add_row("Save JSON", "yes" if config.save_transcript_json else "no")
    table.add_row("Save TXT", "yes" if config.save_transcript_txt else "no")
    table.add_row(
        "Prompt",
        "custom" if config.system_prompt != SYSTEM_PROMPT else "built-in",
    )

    console.print()
    console.print(table)
    console.print()


# ---------------------------------------------------------------------------
# Top-level wizard
# ---------------------------------------------------------------------------

def run_interactive_wizard() -> Config:
    """Run the full interactive setup wizard and return a populated :class:`Config`."""
    console.print(
        Panel(
            "[bold yellow]ClipDigest[/bold yellow] — YouTube Video Summarizer\n"
            "[dim]Answer the questions below to configure your summarization run.[/dim]",
            style="yellow",
        )
    )

    urls = collect_urls()
    model_cfg = collect_model_config()
    system_prompt = collect_prompt_config()
    output_dir, save_json, save_txt = collect_output_config()

    config = Config(
        urls=urls,
        model_config=model_cfg,
        system_prompt=system_prompt,
        output_dir=output_dir,
        save_transcript_json=save_json,
        save_transcript_txt=save_txt,
    )

    show_config_summary(config)

    if not _confirm("Proceed with these settings?", default=True):
        console.print("[yellow]Aborted.[/yellow]")
        raise SystemExit(0)

    return config