"""
Module: CCSDK Core

Core wrapper around AI providers (Claude, GitHub Copilot) with robust error handling.
See README.md for full contract specification.

Basic Usage:
    >>> from amplifier.ccsdk_toolkit.core import CCSDKSession, AIProvider, SessionOptions
    >>> # Use Claude (default)
    >>> async with CCSDKSession(system_prompt="You are a helpful assistant") as session:
    ...     response = await session.query("Hello!")
    
    >>> # Use GitHub Copilot
    >>> options = SessionOptions(provider=AIProvider.COPILOT)
    >>> async with create_session(options) as session:
    ...     response = await session.query("Hello!")
"""

from .base_session import AISession
from .copilot_session import CopilotSession
from .factory import create_session
from .models import AIProvider, SessionOptions, SessionResponse
from .session import ClaudeSession
from .session import ClaudeSession as CCSDKSession  # Alias for requested naming
from .session import SDKNotAvailableError, SessionError
from .utils import check_claude_cli, query_with_retry

__all__ = [
    "CCSDKSession",
    "ClaudeSession",
    "CopilotSession",
    "AISession",
    "SessionError",
    "SDKNotAvailableError",
    "SessionResponse",
    "SessionOptions",
    "AIProvider",
    "check_claude_cli",
    "query_with_retry",
    "create_session",
]
