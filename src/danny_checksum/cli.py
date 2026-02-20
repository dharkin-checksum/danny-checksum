import asyncio
import os

from dotenv import load_dotenv

from danny_checksum.agent import agent
from danny_checksum.github_client import GitHubClient


async def main() -> None:
    load_dotenv()

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token or token.startswith("github_pat_REPLACE"):
        print("Error: Set a valid GITHUB_TOKEN in .env")
        return

    client = GitHubClient.from_token(token)
    conversation_history = []

    print("GitHub Agent (type 'quit' to exit)")
    print("-" * 40)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input or user_input.lower() in ("quit", "exit"):
            print("Bye!")
            break

        result = await agent.run(
            user_input, deps=client, message_history=conversation_history
        )
        conversation_history = result.all_messages()
        print(f"\nAgent: {result.output}")


if __name__ == "__main__":
    asyncio.run(main())
