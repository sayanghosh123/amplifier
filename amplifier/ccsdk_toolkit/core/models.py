"""Data models for CCSDK Core module."""

from collections.abc import Callable
from enum import Enum
from typing import Any

from pydantic import BaseModel
from pydantic import Field


class AIProvider(str, Enum):
    """Supported AI providers."""

    CLAUDE = "claude"
    COPILOT = "copilot"


class SessionOptions(BaseModel):
    """Configuration options for AI sessions.

    Attributes:
        system_prompt: System prompt for the session
        max_turns: Maximum conversation turns (default: unlimited)
        retry_attempts: Number of retry attempts on failure (default: 3)
        retry_delay: Initial retry delay in seconds (default: 1.0)
        stream_output: Enable real-time streaming output (default: False)
        progress_callback: Optional callback for progress updates
        provider: AI provider to use (default: claude)
    """

    system_prompt: str = Field(default="You are a helpful assistant")
    max_turns: int = Field(default=1, gt=0)
    retry_attempts: int = Field(default=3, gt=0, le=10)
    retry_delay: float = Field(default=1.0, gt=0, le=10.0)
    stream_output: bool = Field(default=False, description="Enable real-time streaming output")
    progress_callback: Callable[[str], None] | None = Field(
        default=None,
        description="Optional callback for progress updates",
        exclude=True,  # Exclude from serialization since callables can't be serialized
    )
    provider: AIProvider = Field(
        default=AIProvider.CLAUDE,
        description="AI provider to use (claude or copilot)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "system_prompt": "You are a code review assistant",
                "max_turns": 1,
                "retry_attempts": 3,
                "retry_delay": 1.0,
                "stream_output": False,  # Streaming disabled by default
                "provider": "claude",
            }
        }


class SessionResponse(BaseModel):
    """Response from a Claude session query.

    Attributes:
        content: The response text content
        metadata: Additional metadata about the response
        error: Error message if the query failed
    """

    content: str = Field(default="")
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: str | None = Field(default=None)

    @property
    def success(self) -> bool:
        """Check if the response was successful."""
        return self.error is None and bool(self.content)

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Here's the code review...",
                "metadata": {"tokens": 150, "model": "claude-3"},
                "error": None,
            }
        }
