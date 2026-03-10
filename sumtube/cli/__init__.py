"""CLI entry point for SumTube.

Supports two modes:
  1. **Fully interactive** (default / ``--interactive``): a wizard collects all
     settings, offering to use or override any values found in the environment.
  2. **Non-interactive** (``--no-interactive``): classic argparse flags, useful
     for scripting and CI pipelines.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import dotenv
from rich.console import Console

console = Console()


def _load_env() -> None:
    dotenv.load_dotenv()


# ---------------------------------------------------------------------------
# Non-interactive config builder
# ---------------------------------------------------------------------------

def _build_config_from_args(args) -> "Config":  # noqa: ANN001
    from sumtube.config import Config, ModelConfig, ENV_KEYS

    # Collect URLs
    urls: list[str] = []
    if args.url:
        urls.append(args.url)
    if args.file:
        path = Path(args.file)
        if not path.exists():
            console.print(f"[red]File not found: {path}[/red]")
            sys.exit(1)
        urls.extend(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    if not urls:
        console.print("[red]Provide at least one URL (--url) or a file (--file).[/red]")
        sys.exit(1)

    # API key resolution
    env_key_name = ENV_KEYS.get(args.model_provider)
    api_key = args.api_key or (os.environ.get(env_key_name, "") if env_key_name else None)

    model_cfg = ModelConfig(
        provider=args.model_provider,
        model=args.model,
        api_key=api_key or None,
        extra_kwargs=args.model_kwargs,
    )

    # System prompt
    from sumtube.config import SYSTEM_PROMPT
    system_prompt = SYSTEM_PROMPT
    if args.custom_prompt_file:
        p = Path(args.custom_prompt_file)
        if p.exists():
            system_prompt = p.read_text(encoding="utf-8")
        else:
            console.print(f"[yellow]Prompt file not found: {p}; using built-in.[/yellow]")

    return Config(
        urls=urls,
        model_config=model_cfg,
        system_prompt=system_prompt,
        output_dir=args.output_dir,
        save_transcript_json=not args.no_transcript_json,
        save_transcript_txt=not args.no_transcript_txt,
    )


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser():
    import argparse

    parser = argparse.ArgumentParser(
        prog="sumtube",
        description="SumTube — YouTube Video Summarizer",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Mode
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--interactive", "-i",
        action="store_true",
        default=True,
        help="Run the interactive setup wizard (default).",
    )
    mode.add_argument(
        "--no-interactive", "-I",
        dest="interactive",
        action="store_false",
        help="Skip the wizard and use CLI flags only.",
    )

    # Input
    parser.add_argument("--url", "-u", help="YouTube video URL to summarise.")
    parser.add_argument(
        "--file", "-f",
        help="Path to a file with one YouTube URL per line.",
    )

    # Model
    parser.add_argument("--model", "-m", default="gpt-4o-mini", help="LLM model name.")
    parser.add_argument(
        "--model-provider", "-p",
        dest="model_provider",
        default="openai",
        help="LangChain model provider.",
    )
    parser.add_argument("--api-key", "-k", dest="api_key", default="", help="API key (overrides env var).")
    parser.add_argument(
        "--model-kwargs",
        type=json.loads,
        default="{}",
        help="Extra model keyword arguments as a JSON object.",
    )

    # Prompt
    parser.add_argument(
        "--prompt-file", "-c",
        dest="custom_prompt_file",
        help="Path to a file containing a custom system prompt.",
    )

    # Output
    parser.add_argument("--output-dir", "-o", dest="output_dir", default="outputs", help="Output directory.")
    parser.add_argument(
        "--no-transcript-json",
        action="store_true",
        help="Do not save the raw transcript JSON.",
    )
    parser.add_argument(
        "--no-transcript-txt",
        action="store_true",
        help="Do not save the plain-text transcript.",
    )

    return parser


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    _load_env()

    parser = _build_parser()
    args = parser.parse_args()

    if args.interactive and not (args.url or args.file):
        # Full wizard
        from sumtube.cli.wizard import run_interactive_wizard
        config = run_interactive_wizard()
    else:
        from sumtube.cli.wizard import show_config_summary
        config = _build_config_from_args(args)
        show_config_summary(config)

    from sumtube.cli.pipeline import run
    run(config)


if __name__ == "__main__":
    main()
