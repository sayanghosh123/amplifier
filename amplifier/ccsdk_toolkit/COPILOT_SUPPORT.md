# GitHub Copilot CLI Agent Support

The CCSDK Toolkit now supports GitHub Copilot CLI in addition to Claude Code SDK, allowing you to choose your preferred AI provider.

## Overview

The toolkit provides a unified interface for working with multiple AI providers:
- **Claude Code SDK** - The original provider (default)
- **GitHub Copilot CLI** - New support for GitHub's first-party CLI agent

## Prerequisites

### For GitHub Copilot

You need one of the following:

1. **Standalone Copilot CLI** (recommended for automation)
   - Install from: https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-in-the-command-line
   - Command: `copilot`

2. **GitHub CLI with Copilot extension**
   - Install GitHub CLI: https://cli.github.com/
   - Install extension: `gh extension install github/gh-copilot`
   - Command: `gh copilot`

You also need an active GitHub Copilot subscription.

### For Claude (existing support)

- Claude CLI installed: `npm install -g @anthropic-ai/claude-code`
- Or: `bun install -g @anthropic-ai/claude-code`

## Usage

### Basic Usage - Direct Session Creation

```python
import asyncio
from amplifier.ccsdk_toolkit import CopilotSession, SessionOptions

async def main():
    options = SessionOptions(
        system_prompt="You are a helpful coding assistant",
        stream_output=True,
    )
    
    async with CopilotSession(options) as session:
        response = await session.query("Explain what a Python decorator is")
        
        if response.success:
            print(response.content)
        else:
            print(f"Error: {response.error}")

asyncio.run(main())
```

### Factory Pattern - Provider Selection

Use the factory pattern to dynamically select providers:

```python
import asyncio
from amplifier.ccsdk_toolkit import create_session, AIProvider, SessionOptions

async def main():
    # Configure with Copilot
    options = SessionOptions(
        provider=AIProvider.COPILOT,
        system_prompt="You are a helpful assistant",
    )
    
    # Factory creates appropriate session based on provider
    async with create_session(options) as session:
        response = await session.query("Write a Python function to calculate fibonacci")
        print(response.content)

asyncio.run(main())
```

### Comparing Providers

You can easily compare responses from different providers:

```python
import asyncio
from amplifier.ccsdk_toolkit import create_session, AIProvider, SessionOptions

async def compare_providers(question: str):
    for provider in [AIProvider.CLAUDE, AIProvider.COPILOT]:
        print(f"\n=== Using {provider.value.upper()} ===")
        
        options = SessionOptions(provider=provider)
        
        try:
            async with create_session(options) as session:
                response = await session.query(question)
                if response.success:
                    print(response.content[:200] + "...")
                else:
                    print(f"Error: {response.error}")
        except Exception as e:
            print(f"Provider not available: {e}")

asyncio.run(compare_providers("What is the difference between a list and tuple in Python?"))
```

## CLI Tool Templates

The CLI builder templates now support provider selection via command-line flag:

```bash
# Using Claude (default)
./my_tool.py "analyze this code"

# Using Copilot
./my_tool.py "analyze this code" --provider copilot
```

### Building New Tools with Provider Support

```python
from amplifier.ccsdk_toolkit import CliBuilder, CliTemplate

builder = CliBuilder()
builder.create_tool(
    name="my-analyzer",
    template=CliTemplate.BASIC,
    description="Code analysis tool with AI provider selection",
    system_prompt="You are a code analysis expert"
)
```

The generated tool will automatically include `--provider` option for runtime selection.

## Configuration

### Environment-Based Provider Selection

You can set a default provider via environment variable:

```bash
export AMPLIFIER_AI_PROVIDER=copilot  # Future enhancement
```

### In SessionOptions

```python
from amplifier.ccsdk_toolkit import SessionOptions, AIProvider

# Explicit provider selection
options = SessionOptions(
    provider=AIProvider.COPILOT,  # or AIProvider.CLAUDE
    system_prompt="You are helpful",
    max_turns=1,
    retry_attempts=3,
    stream_output=True,
)
```

## API Reference

### AIProvider Enum

```python
from amplifier.ccsdk_toolkit import AIProvider

AIProvider.CLAUDE   # Claude Code SDK (default)
AIProvider.COPILOT  # GitHub Copilot CLI
```

### CopilotSession Class

Similar interface to `ClaudeSession`:

```python
class CopilotSession(AISession):
    """Async context manager for GitHub Copilot CLI sessions."""
    
    async def query(self, prompt: str, stream: bool | None = None) -> SessionResponse:
        """Send a query to GitHub Copilot CLI."""
```

### Factory Function

```python
def create_session(options: SessionOptions | None = None) -> AISession:
    """Create an AI session based on the provider in options."""
```

## Error Handling

Both providers use the same error handling approach:

```python
from amplifier.ccsdk_toolkit import create_session, SDKNotAvailableError

try:
    async with create_session(options) as session:
        response = await session.query("test")
except SDKNotAvailableError as e:
    print(f"Provider not available: {e}")
    # Error message includes installation instructions
```

## Examples

See `amplifier/ccsdk_toolkit/examples/copilot_example.py` for complete working examples:

```bash
cd amplifier/ccsdk_toolkit/examples
python copilot_example.py
```

## Limitations and Differences

### GitHub Copilot CLI
- Stateless CLI invocations (no persistent session state)
- May have different response formats than Claude
- Depends on GitHub Copilot subscription status
- Tool/function calling may not be supported (depends on CLI version)

### Claude Code SDK
- Stateful sessions with full SDK integration
- Rich tool/function calling support
- Session persistence and resumption
- More control over model parameters

## Migration Guide

### Existing Code Using ClaudeSession

No changes needed - existing code continues to work:

```python
# This still works unchanged
from amplifier.ccsdk_toolkit import ClaudeSession

async with ClaudeSession(options) as session:
    response = await session.query("test")
```

### Adding Copilot Support to Existing Code

Minimal changes to add provider selection:

```python
# Before
from amplifier.ccsdk_toolkit import ClaudeSession
async with ClaudeSession(options) as session:
    ...

# After - with provider selection
from amplifier.ccsdk_toolkit import create_session, AIProvider
options.provider = AIProvider.COPILOT  # Add provider selection
async with create_session(options) as session:
    ...
```

## Troubleshooting

### "GitHub Copilot CLI not found"

**Solution**: Install Copilot CLI or GitHub CLI with extension:
```bash
# Option 1: Via GitHub CLI
gh extension install github/gh-copilot

# Option 2: Standalone (follow GitHub docs)
```

### "Authentication required"

**Solution**: Authenticate with GitHub:
```bash
gh auth login
```

### Different Response Formats

The response format may differ between providers. Both return `SessionResponse` objects, but content structure might vary based on the provider's output format.

## Future Enhancements

Planned improvements:
- [ ] Auto-detection of available providers
- [ ] Environment-based default provider configuration
- [ ] Provider-specific configuration options
- [ ] Streaming support improvements for Copilot
- [ ] Tool/function calling abstraction across providers
- [ ] Cost/usage tracking per provider

## Contributing

When adding support for new providers:
1. Create a new session class extending `AISession`
2. Implement required abstract methods
3. Add provider to `AIProvider` enum
4. Update factory function
5. Add tests and documentation

See `amplifier/ccsdk_toolkit/core/base_session.py` for the interface definition.
