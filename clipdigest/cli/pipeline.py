"""Core pipeline: fetch metadata, transcript, summarise, and save."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from clipdigest.config import Config
from clipdigest.models import get_model, summarize
from clipdigest.output import format_summary, make_output_dir, save_text
from clipdigest.transcript import fetch_transcript, transcript_to_json, transcript_to_text
from clipdigest.transcript.metadata import get_video_metadata

console = Console()


def process_video(url: str, config: Config) -> Path:
    """Fetch, summarise, and save a single YouTube video.

    Args:
        url: YouTube video URL.
        config: Resolved :class:`~clipdigest.config.Config`.

    Returns:
        Path to the directory where outputs were saved.
    """
    base_output = Path(config.output_dir)

    # 1. Metadata
    console.print(f"  [dim]→[/dim] Fetching video metadata…")
    metadata = get_video_metadata(url)
    console.print(f"  [green]✓[/green] [bold]{metadata.get('title', url)}[/bold]")

    output_dir = make_output_dir(base_output, metadata)

    # 2. Transcript
    console.print(f"  [dim]→[/dim] Fetching transcript…")
    transcript = fetch_transcript(url, languages=config.transcript_languages)
    console.print(f"  [green]✓[/green] Transcript fetched ({len(transcript.snippets)} snippets)")

    if config.save_transcript_json:
        save_text(transcript_to_json(transcript), output_dir / "transcript.json")
        console.print("  [dim]  Saved transcript.json[/dim]")

    transcript_text = transcript_to_text(transcript)

    if config.save_transcript_txt:
        save_text(transcript_text, output_dir / "transcript.txt")
        console.print("  [dim]  Saved transcript.txt[/dim]")

    # 3. Summarise
    console.print(f"  [dim]→[/dim] Summarising with [bold]{config.model_config.model}[/bold]…")
    model = get_model()
    raw_summary = summarize(
        transcript_text,
        model=model,
        system_prompt=config.system_prompt,
    )

    # 4. Format + save
    full_doc = format_summary(raw_summary, metadata, url)
    from pathvalidate import sanitize_filename
    safe_title = sanitize_filename(str(metadata.get("title", "summary")))
    summary_path = output_dir / f"{safe_title}.md"
    save_text(full_doc, summary_path)
    console.print(f"  [green]✓[/green] Summary saved → [bold]{summary_path}[/bold]")

    return output_dir


def run(config: Config) -> None:
    """Process all URLs in *config* sequentially."""
    from clipdigest.models import init_model

    init_model(config.model_config)

    total = len(config.urls)
    console.print()
    for i, url in enumerate(config.urls, 1):
        console.rule(f"[bold]Video {i}/{total}[/bold]")
        try:
            process_video(url, config)
        except Exception as exc:  # noqa: BLE001
            console.print(f"  [red]✗ Error processing {url}: {exc}[/red]")
        console.print()

    console.rule("[green bold]All done![/green bold]")