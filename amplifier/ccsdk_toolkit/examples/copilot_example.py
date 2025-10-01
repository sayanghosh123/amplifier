#!/usr/bin/env python3
"""
Example demonstrating GitHub Copilot CLI integration with CCSDK toolkit.

This example shows how to use the CopilotSession class to interact with
GitHub Copilot CLI for code assistance.

Requirements:
    - GitHub Copilot CLI installed (copilot command or gh copilot)
    - Active GitHub Copilot subscription

Install Copilot CLI:
    - Standalone: See https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-in-the-command-line
    - Via GitHub CLI: gh extension install github/gh-copilot
"""

import asyncio

from amplifier.ccsdk_toolkit import (
    AIProvider,
    CopilotSession,
    SessionOptions,
    create_session,
)


async def example_direct_copilot():
    """Example using CopilotSession directly."""
    print("=" * 60)
    print("Example 1: Using CopilotSession directly")
    print("=" * 60)

    options = SessionOptions(
        system_prompt="You are a helpful coding assistant",
        stream_output=True,
    )

    try:
        async with CopilotSession(options) as session:
            response = await session.query(
                "Explain what a Python decorator is in simple terms"
            )

            if response.success:
                print(f"\n✓ Success! Got response ({len(response.content)} chars)")
            else:
                print(f"\n✗ Error: {response.error}")

    except Exception as e:
        print(f"\n✗ Exception: {e}")


async def example_factory_pattern():
    """Example using factory pattern with provider selection."""
    print("\n" + "=" * 60)
    print("Example 2: Using factory pattern with provider selection")
    print("=" * 60)

    # Create options with Copilot provider
    options = SessionOptions(
        provider=AIProvider.COPILOT,
        system_prompt="You are a helpful assistant",
        stream_output=True,
    )

    try:
        # Factory automatically creates CopilotSession based on provider
        async with create_session(options) as session:
            response = await session.query(
                "Write a Python function to calculate fibonacci numbers"
            )

            if response.success:
                print(f"\n✓ Success! Got response ({len(response.content)} chars)")
                if response.metadata:
                    print(f"Provider: {response.metadata.get('provider', 'unknown')}")
            else:
                print(f"\n✗ Error: {response.error}")

    except Exception as e:
        print(f"\n✗ Exception: {e}")


async def example_compare_providers():
    """Example comparing responses from both providers."""
    print("\n" + "=" * 60)
    print("Example 3: Comparing Claude vs Copilot")
    print("=" * 60)

    question = "What is the difference between a list and a tuple in Python?"

    # Try both providers
    for provider in [AIProvider.CLAUDE, AIProvider.COPILOT]:
        print(f"\n--- Using {provider.value.upper()} ---")

        options = SessionOptions(
            provider=provider,
            stream_output=False,  # Disable streaming for cleaner output
        )

        try:
            async with create_session(options) as session:
                response = await session.query(question)

                if response.success:
                    print(f"✓ Response from {provider.value}:")
                    print(response.content[:200] + "..." if len(response.content) > 200 else response.content)
                else:
                    print(f"✗ Error from {provider.value}: {response.error}")

        except Exception as e:
            print(f"✗ {provider.value} not available: {e}")


async def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("GitHub Copilot CLI Integration Examples")
    print("=" * 60)

    # Run examples
    await example_direct_copilot()
    await example_factory_pattern()
    await example_compare_providers()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
