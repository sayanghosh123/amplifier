"""GitHub Copilot CLI session implementation."""

import asyncio
import json
import shutil
import subprocess
from typing import Any

from .base_session import AISession
from .models import SessionOptions, SessionResponse
from .session import SDKNotAvailableError, SessionError


class CopilotSession(AISession):
    """Async context manager for GitHub Copilot CLI sessions.

    This provides a wrapper around the GitHub Copilot CLI with:
    - Prerequisite checking for the copilot or gh CLI
    - Automatic retry with exponential backoff
    - Graceful error handling
    """

    def __init__(self, options: SessionOptions | None = None):
        """Initialize session with options.

        Args:
            options: Session configuration options
        """
        super().__init__(options)
        self._check_prerequisites()
        self._copilot_command = None

    def _check_prerequisites(self):
        """Check if copilot CLI or gh CLI is installed and accessible."""
        # Check for standalone copilot CLI
        copilot_path = shutil.which("copilot")
        if copilot_path:
            self._copilot_command = ["copilot"]
            return

        # Check for GitHub CLI with copilot extension
        gh_path = shutil.which("gh")
        if gh_path:
            # Verify gh copilot extension is available
            try:
                result = subprocess.run(
                    ["gh", "copilot", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    self._copilot_command = ["gh", "copilot"]
                    return
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                pass

        # Neither option worked
        raise SDKNotAvailableError(
            "GitHub Copilot CLI not found. Install with one of:\n"
            "  - Install GitHub Copilot CLI: see https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-in-the-command-line\n"
            "  - Or install GitHub CLI: see https://cli.github.com/\n"
            "  Then install copilot extension: gh extension install github/gh-copilot"
        )

    async def __aenter__(self):
        """Enter async context and initialize."""
        # Copilot CLI is stateless, no client to initialize
        # Just verify command is still available
        if not self._copilot_command:
            self._check_prerequisites()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context and cleanup."""
        # No cleanup needed for stateless CLI
        pass

    async def query(self, prompt: str, stream: bool | None = None) -> SessionResponse:
        """Send a query to GitHub Copilot CLI.

        Args:
            prompt: The prompt to send to Copilot
            stream: Override the session's stream_output setting (streaming not fully supported yet)

        Returns:
            SessionResponse with the result or error
        """
        if not self._copilot_command:
            return SessionResponse(error="Session not initialized properly.")

        retry_delay = self.options.retry_delay
        last_error = None

        for attempt in range(self.options.retry_attempts):
            try:
                # Prepare the command
                # Note: The actual command structure may vary based on Copilot CLI version
                # Using a basic approach: pass prompt as argument
                cmd = self._copilot_command + ["explain", prompt]

                # Execute command
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    stdin=asyncio.subprocess.PIPE,
                )

                stdout, stderr = await process.communicate()

                if process.returncode == 0:
                    response_text = stdout.decode("utf-8").strip()
                    
                    # Stream output if enabled
                    should_stream = stream if stream is not None else self.options.stream_output
                    if should_stream and response_text:
                        print(response_text)
                        print()  # Final newline

                    # Call progress callback if provided
                    if self.options.progress_callback and response_text:
                        self.options.progress_callback(response_text)

                    metadata: dict[str, Any] = {
                        "attempt": attempt + 1,
                        "provider": "copilot",
                    }

                    if response_text:
                        return SessionResponse(content=response_text, metadata=metadata)

                    # Empty response, will retry
                    raise ValueError("Received empty response from Copilot CLI")
                else:
                    # Command failed
                    error_msg = stderr.decode("utf-8").strip()
                    raise SessionError(f"Copilot CLI error: {error_msg}")

            except ValueError as e:
                last_error = str(e)
            except Exception as e:
                last_error = str(e)

            # Wait before retry (except on last attempt)
            if attempt < self.options.retry_attempts - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff

        # All retries exhausted
        return SessionResponse(
            error=f"Failed after {self.options.retry_attempts} attempts: {last_error}"
        )
