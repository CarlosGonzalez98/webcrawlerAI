from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.globals import get_llm_cache
from langchain_core.language_models.base import (
    BaseLanguageModel,
    LangSmithParams,
    LanguageModelInput,
)
import os
from langchain_core.load import dumpd, dumps
from langchain_core.messages import (
    AIMessage,
    SystemMessage,
    AnyMessage,
    BaseMessage,
    BaseMessageChunk,
    HumanMessage,
    convert_to_messages,
    message_chunk_to_message,
)
from langchain_core.outputs import (
    ChatGeneration,
    ChatGenerationChunk,
    ChatResult,
    LLMResult,
    RunInfo,
)
from langchain_core.output_parsers.base import OutputParserLike
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.tools import BaseTool

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Literal,
    Optional,
    Union,
    cast, List,
)
from pydantic import SecretStr

from src.utils import config


def get_llm_model(provider: str, **kwargs):
    """
    Get LLM model
    :param provider: LLM provider (only 'openai' is supported)
    :param kwargs:
    :return:
    """
    # Always use OpenAI
    env_var = "OPENAI_API_KEY"
    api_key = kwargs.get("api_key", "") or os.getenv(env_var, "")
    if not api_key:
        error_msg = f"💥 OpenAI API key not found! 🔑 Please set the `{env_var}` environment variable or provide it in the UI."
        raise ValueError(error_msg)
    if isinstance(api_key, str):
        api_key = SecretStr(api_key)
        kwargs["api_key"] = api_key

    # Configure OpenAI endpoint
    base_url = kwargs.get("base_url", "") or os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1")

    return ChatOpenAI(
            model=kwargs.get("model_name", "gpt-4o"),
            temperature=kwargs.get("temperature", 0.0),
            base_url=base_url,
            api_key=api_key,
        )
