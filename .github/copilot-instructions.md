# GitHub Copilot Instructions

This file provides guidance to GitHub Copilot when working with code in this repository.

## Project Overview

Amplifier is a complete development environment that supercharges AI coding assistants with discovered patterns, specialized expertise, and powerful automation. This project is designed for AI-assisted development with a focus on modular architecture and ruthless simplicity.

## Important Context Files

Before making significant changes, consult these files:

- **AGENTS.md** - Core guidelines for AI assistants, build commands, code style, and design philosophy
- **DISCOVERIES.md** - Known issues and solutions (check before debugging complex problems)
- **ai_working/decisions/** - Architectural decision records (understand context before changing patterns)

## Core Development Principles

### 1. Ruthless Simplicity

- Keep everything as simple as possible, but no simpler
- Minimize abstractions - every layer must justify its existence
- Start minimal, grow as needed - don't build for hypothetical future requirements
- Question everything - regularly challenge complexity in the codebase

### 2. Zero-BS Principle: No Stubs or Placeholders

**CRITICAL**: Never create functions, classes, or files that are incomplete or don't work.

❌ **NEVER do this:**
```python
def process_payment(amount):
    # TODO: Implement Stripe integration
    raise NotImplementedError("Payment processing coming soon")
```

✅ **ALWAYS do this:**
```python
def process_payment(amount, payments_file="payments.json"):
    """Record payment to local file - fully functional."""
    payment = {"amount": amount, "timestamp": datetime.now().isoformat()}
    
    if Path(payments_file).exists():
        with open(payments_file) as f:
            payments = json.load(f)
    else:
        payments = []
    
    payments.append(payment)
    with open(payments_file, 'w') as f:
        json.dump(payments, f)
    
    return payment
```

**Rule**: Every function must work or not exist. Every file must be complete or not created.

### 3. Modular Design Philosophy

Think "bricks & studs":
- **Brick** = self-contained directory that delivers one clear responsibility
- **Stud** = public contract (function signatures, CLI, API schema) that other bricks latch onto

**Process**:
1. Always start with the contract (document purpose, inputs, outputs, side-effects, dependencies)
2. Build the brick in isolation with tests
3. Expose only the contract via `__all__` or interface file
4. When changes are needed, regenerate the whole brick from its spec rather than patching

## Build, Test, and Lint Commands

```bash
# Install dependencies
make install

# Add new dependencies (use uv, never edit pyproject.toml manually)
uv add package-name

# Add development dependencies
uv add --dev package-name

# Run all checks (lint, format, type check)
make check

# Run all tests
make test

# Run a specific test
uv run pytest tests/path/to/test_file.py::TestClass::test_function -v

# Upgrade dependency lock
make lock-upgrade
```

## Code Style Guidelines

### Python Style

- **Always use type hints** consistently, including for `self` in class methods
- **Import organization**: Standard lib → Third-party → Local
- **Use descriptive names**: `get_workspace` not `gw`
- **Use `Optional`** from typing for optional parameters
- **Python 3.11+** compatibility required
- **Use Pydantic** for data validation and settings

### Formatting

- **Line length**: 120 characters (configured in ruff.toml)
- **File endings**: All files must end with a newline character (add blank line at EOF)
- **Type ignores**: Use `# type: ignore` for Reflex dynamic methods, `# pyright: ignore[specificError]` for complex cases
- **Ruff**: Project uses ruff for formatting and linting (settings in `ruff.toml`)

### File Organization

- **DO NOT add files to `/tools` directory** - reserved for specific build tools
- Organize code into proper module directories
- Keep utility scripts with their related modules

## Configuration Management: Single Source of Truth

Every configuration setting should have exactly ONE authoritative location:

- **pyproject.toml** - Python project settings (primary)
- **ruff.toml** - Ruff-specific settings only if not in pyproject.toml
- **.vscode/settings.json** - IDE settings that reference project config
- **Makefile** - Commands that use project config, not duplicate it

✅ **Good**: Read from authoritative source
```python
config = tomllib.load(open("pyproject.toml", "rb"))
excludes = config["tool"]["pyright"]["exclude"]
```

❌ **Bad**: Hardcode values
```python
excludes = [".venv", "__pycache__", "node_modules"]
```

## Testing Requirements

After making code changes, you MUST:

1. **Run `make check`** - Catches syntax, linting, and type errors
2. **Start the affected service** - Catches runtime errors and invalid API usage
3. **Test basic functionality** - Send a test request or verify service starts cleanly
4. **Stop the service** - Use Ctrl+C or kill process to free up ports

### Common Runtime Errors Not Caught by `make check`

- Invalid API calls to external libraries
- Import errors from circular dependencies
- Configuration/environment variable issues
- Port conflicts and service startup failures

## Incremental Processing Pattern

When building batch processing systems:

- **Save continuously**: Write results after each item, not at intervals or only at completion
- **Fixed filenames**: Use consistent filenames (e.g., `results.json`) that overwrite, not timestamps
- **Enable interruption**: Users can abort anytime without losing processed items
- **Support incremental updates**: New items can be added without reprocessing existing ones

The bottleneck is always the processing (LLM APIs, network calls), never disk I/O.

## Decision Tracking

Before proposing major changes:

1. **Check `ai_working/decisions/`** for relevant architectural decisions
2. **Understand the rationale** behind existing patterns
3. **Create new decision records** for significant architectural choices

Decisions CAN change, but should change with full understanding of why they were originally made.

## Response Authenticity Guidelines

### Professional Communication Without Sycophancy

Be professional and helpful without being:
- Overly deferential or praise-heavy
- Artificially enthusiastic
- Unnecessarily apologetic

❌ **Avoid**: "Wow, that's an excellent question! I'm so glad you asked! Let me help you with that amazing idea..."

✅ **Instead**: "I can help with that. Here's the approach..."

## Library Usage Philosophy

- **Use libraries as intended**: Minimal wrappers around external libraries
- **Direct integration**: Avoid unnecessary adapter layers
- **Selective dependency**: Add dependencies only when they provide substantial value
- **Understand what you import**: No black-box dependencies

## Technical Implementation Guidelines

### API Layer
- Implement only essential endpoints
- Minimal middleware with focused validation
- Clear error responses with useful messages
- Consistent patterns across endpoints

### Database & Storage
- Simple schema focused on current needs
- Use TEXT/JSON fields to avoid excessive normalization early
- Add indexes only when needed for performance
- Delay complex database features until required

### MCP Implementation
- Streamlined MCP client with minimal error handling
- Utilize FastMCP when possible, falling back to lower-level only when necessary
- Focus on core functionality without elaborate state management
- Implement only essential health checks

### SSE & Real-time Updates
- Basic SSE connection management
- Simple resource-based subscriptions
- Direct event delivery without complex routing
- Minimal state tracking for connections

## Remember

- It's easier to add complexity later than to remove it
- Code you don't write has no bugs
- Favor clarity over cleverness
- The best code is often the simplest
- Trust in emergence: complex systems work best when built from simple, well-defined components

## Additional Resources

For detailed implementation philosophy and patterns, see:
- `ai_context/IMPLEMENTATION_PHILOSOPHY.md`
- `ai_context/MODULAR_DESIGN_PHILOSOPHY.md`
