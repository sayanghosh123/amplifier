"""Abstract base class for AI session implementations."""

from abc import ABC, abstractmethod
from typing import Any

from .models import SessionOptions, SessionResponse


class AISession(ABC):
    """Abstract base class for AI provider sessions.
    
    This defines the interface that all AI provider implementations must follow.
    Concrete implementations include ClaudeSession and CopilotSession.
    """

    def __init__(self, options: SessionOptions | None = None):
        """Initialize session with options.

        Args:
            options: Session configuration options
        """
        self.options = options or SessionOptions()
        self.client: Any | None = None

    @abstractmethod
    def _check_prerequisites(self):
        """Check if the provider's CLI/SDK is installed and accessible.
        
        Raises:
            SDKNotAvailableError: If prerequisites are not met
        """
        pass

    @abstractmethod
    async def __aenter__(self):
        """Enter async context and initialize the provider client.
        
        Returns:
            Self for context manager
            
        Raises:
            SDKNotAvailableError: If the provider is not available
        """
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context and cleanup."""
        pass

    @abstractmethod
    async def query(self, prompt: str, stream: bool | None = None) -> SessionResponse:
        """Send a query to the AI provider.

        Args:
            prompt: The prompt to send
            stream: Override the session's stream_output setting

        Returns:
            SessionResponse with the result or error
        """
        pass
