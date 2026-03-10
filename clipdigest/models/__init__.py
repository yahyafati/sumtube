"""LLM initialisation and transcript summarisation."""

from __future__ import annotations

from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from clipdigest.config import ModelConfig, SYSTEM_PROMPT

_model_instance: Optional[BaseChatModel] = None


def init_model(model_cfg: ModelConfig) -> BaseChatModel:
    """Initialise (and cache) the LangChain chat model described by *model_cfg*."""
    global _model_instance

    from langchain.chat_models import init_chat_model

    kwargs = dict(model_cfg.extra_kwargs)
    if model_cfg.api_key:
        kwargs["api_key"] = model_cfg.api_key

    _model_instance = init_chat_model(
        model=model_cfg.model,
        model_provider=model_cfg.provider,
        **kwargs,
    )
    return _model_instance


def get_model() -> BaseChatModel:
    """Return the cached model, raising if it has not been initialised yet."""
    if _model_instance is None:
        raise RuntimeError("Model has not been initialised. Call init_model() first.")
    return _model_instance


def reset_model() -> None:
    """Clear the cached model (useful for tests or re-configuration)."""
    global _model_instance
    _model_instance = None


def summarize(
    transcript_text: str,
    *,
    model: Optional[BaseChatModel] = None,
    system_prompt: str = SYSTEM_PROMPT,
) -> str:
    """Summarise *transcript_text* using *model* (or the cached model).

    Args:
        transcript_text: Plain-text transcript to summarise.
        model: Optional explicit model instance; falls back to the cached one.
        system_prompt: System prompt to use; defaults to :data:`~clipdigest.config.SYSTEM_PROMPT`.

    Returns:
        The model's summary as a plain string.
    """
    if model is None:
        model = get_model()

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Please summarize the following transcript:\n\n{transcript_text}"),
    ])
    response = model.invoke(prompt_template.invoke({"transcript_text": transcript_text}))

    if isinstance(response, str):
        return response
    # LangChain AIMessage → .content may be str or list[dict]
    content = response.content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return str(content)
