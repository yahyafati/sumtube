"""YouTube video metadata retrieval."""

from __future__ import annotations

from yt_dlp import YoutubeDL

_WANTED_FIELDS = (
    "id", "title", "uploader", "upload_date", "duration",
    "view_count", "like_count", "channel_url", "description",
    "categories", "tags", "webpage_url", "thumbnail",
)


def get_video_metadata(url: str) -> dict[str, object]:
    """Return a dictionary of video metadata for *url*.

    Only a curated subset of yt-dlp's full info dict is returned.
    """
    ydl_opts = {
        "skip_download": True,
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True,
        "extractor_args": {"youtube": {"player_client": ["default"]}},
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    return {field: info.get(field) for field in _WANTED_FIELDS}


def format_duration(seconds: int | None) -> str:
    """Convert a duration in seconds to a human-readable ``HH:MM:SS`` string."""
    if seconds is None:
        return "unknown"
    h, remainder = divmod(int(seconds), 3600)
    m, s = divmod(remainder, 60)
    if h:
        return f"{h}h {m:02d}m {s:02d}s"
    return f"{m}m {s:02d}s"


def format_upload_date(raw: str | None) -> str:
    """Convert a ``YYYYMMDD`` string to ``YYYY-MM-DD``."""
    if raw and len(raw) == 8:
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:]}"
    return raw or "unknown"