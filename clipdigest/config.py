"""Configuration dataclasses and constants for ClipDigest."""

from __future__ import annotations

import dataclasses
from typing import Optional


SYSTEM_PROMPT = """\
You are an expert summarizer specializing in extracting key insights from spoken content \
such as lectures, interviews, and documentaries.
Your goal is to produce informative, concise, and accurate summaries from raw YouTube transcripts.

Instructions:
1. Comprehension: Read the entire transcript carefully to understand the main topic, structure, and arguments.
2. Summarization:
    - Capture the main ideas, key arguments, and important details.
    - Preserve factual accuracy and the speaker's intent.
    - Avoid filler words, introductions, or repetition.
3. Style:
    - Write in clear, objective, and neutral tone.
    - Use short paragraphs or bullet points if appropriate.
    - Make it informative, not just brief — focus on what was said and why it matters.
4. Output:
    - Produce a 1–3 paragraph summary (or longer for very detailed videos).
    - Optionally include a short list of key takeaways if helpful.

Example Output:
### Summary
[Concise yet detailed summary of the transcript's main ideas.]

### Key Takeaways
- [Main point 1]: [Explanation]
- [Main point 2]
    [Detailed explanation if needed]
- [Main point 3]
"""

SUPPORTED_PROVIDERS = [
    "openai",
    "anthropic",
    "google_genai",
    "azure_openai",
    "ollama",
    "groq",
    "mistralai",
]

DEFAULT_MODELS: dict[str, str] = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-20241022",
    "google_genai": "gemini-2.0-flash",
    "azure_openai": "gpt-4o-mini",
    "ollama": "llama3.2",
    "groq": "llama-3.3-70b-versatile",
    "mistralai": "mistral-small-latest",
}

ENV_KEYS: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google_genai": "GOOGLE_API_KEY",
    "azure_openai": "AZURE_OPENAI_API_KEY",
    "groq": "GROQ_API_KEY",
    "mistralai": "MISTRAL_API_KEY",
    "ollama": None,  # no key needed
}


@dataclasses.dataclass
class ModelConfig:
    provider: str
    model: str
    api_key: Optional[str] = None
    extra_kwargs: dict = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class Config:
    # Input
    urls: list[str] = dataclasses.field(default_factory=list)

    # Model
    model_config: Optional[ModelConfig] = None

    # Prompt
    system_prompt: str = SYSTEM_PROMPT

    # Output
    output_dir: str = "outputs"
    save_transcript_json: bool = True
    save_transcript_md: bool = True

    # Transcript
    transcript_languages: list[str] = dataclasses.field(default_factory=lambda: ["en"])