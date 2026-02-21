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
