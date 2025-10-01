"""Factory for creating AI sessions based on provider."""

from .base_session import AISession
from .copilot_session import CopilotSession
from .models import AIProvider, SessionOptions
from .session import ClaudeSession


def create_session(options: SessionOptions | None = None) -> AISession:
    """Create an AI session based on the provider in options.

    Args:
        options: Session configuration options (provider field determines which session to create)

    Returns:
        AISession instance (ClaudeSession or CopilotSession)

    Raises:
        ValueError: If an unsupported provider is specified
    """
    opts = options or SessionOptions()
    
    if opts.provider == AIProvider.CLAUDE:
        return ClaudeSession(opts)
    elif opts.provider == AIProvider.COPILOT:
        return CopilotSession(opts)
    else:
        raise ValueError(f"Unsupported provider: {opts.provider}")
