"""YouTube transcript fetching and processing utilities."""

from __future__ import annotations

import json
import re

from youtube_transcript_api import FetchedTranscript, YouTubeTranscriptApi


def get_video_id(url: str) -> str:
    """Extract the 11-character video ID from a variety of YouTube URL formats."""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})(?:[&?\/]|$)"
    match = re.search(pattern, url)
    if not match:
        raise ValueError(f"Could not extract a valid video ID from URL: {url!r}")
    return match.group(1)


def fetch_transcript(url: str, languages: list[str] | None = None) -> FetchedTranscript:
    """Fetch the transcript for a YouTube video.

    Args:
        url: YouTube video URL.
        languages: Ordered list of preferred language codes. Defaults to ``["en"]``.

    Returns:
        A :class:`FetchedTranscript` instance.
    """
    if languages is None:
        languages = ["en"]
    video_id = get_video_id(url)
    api = YouTubeTranscriptApi()
    return api.fetch(video_id, languages=languages)


def transcript_to_json(transcript: FetchedTranscript) -> str:
    """Serialise a transcript to a JSON string."""
    return json.dumps(transcript.to_raw_data(), ensure_ascii=False, indent=2)


def transcript_to_text(transcript: FetchedTranscript) -> str:
    """Join all snippet texts into a single plain-text string."""
    return " ".join(snippet.text for snippet in transcript.snippets)
