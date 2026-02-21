from dataclasses import dataclass

from slack_sdk import WebClient


@dataclass
class SlackClient:
    client: WebClient

    @classmethod
    def from_token(cls, token: str) -> "SlackClient":
        return cls(client=WebClient(token=token))

    def list_channels(self, limit: int = 200, types: str = "public_channel") -> str:
        result = self.client.conversations_list(limit=limit, types=types)
        channels = result.get("channels", [])
        lines = []
        for ch in channels:
            prefix = "#" if not ch.get("is_private") else "🔒"
            lines.append(f"{prefix}{ch['name']} (id: {ch['id']}, members: {ch.get('num_members', '?')})")
        return "\n".join(lines) if lines else "No channels found."

    def join_channel(self, channel_id: str) -> str:
        self.client.conversations_join(channel=channel_id)
        return f"Joined channel {channel_id}."

    def read_messages(self, channel_id: str, limit: int = 50) -> str:
        self.client.conversations_join(channel=channel_id)
        result = self.client.conversations_history(channel=channel_id, limit=limit)
        messages = result.get("messages", [])
        lines = []
        for msg in reversed(messages):
            user = msg.get("user", "unknown")
            text = msg.get("text", "")
            ts = msg.get("ts", "")
            lines.append(f"[{ts}] {user}: {text}")
        return "\n".join(lines) if lines else "No messages found."

    def post_message(self, channel_id: str, text: str, thread_ts: str | None = None) -> dict:
        """Post a message to a channel, optionally in a thread. Returns result data."""
        result = self.client.chat_postMessage(
            channel=channel_id, text=text, thread_ts=thread_ts
        )
        return result.data

    def read_thread_replies(
        self, channel_id: str, thread_ts: str, oldest: str | None = None
    ) -> list[dict]:
        """Fetch thread replies, stripping the parent message."""
        kwargs = {"channel": channel_id, "ts": thread_ts}
        if oldest is not None:
            kwargs["oldest"] = oldest
        result = self.client.conversations_replies(**kwargs)
        messages = result.get("messages", [])
        # The first message is the parent; return only replies
        return [m for m in messages if m.get("ts") != thread_ts]

    def get_bot_user_id(self) -> str:
        """Return the bot's own user_id via auth.test."""
        result = self.client.auth_test()
        return result["user_id"]

    def get_channel_name(self, channel_id: str) -> str:
        """Return the human-readable channel name for a channel ID."""
        result = self.client.conversations_info(channel=channel_id)
        return result["channel"]["name"]
