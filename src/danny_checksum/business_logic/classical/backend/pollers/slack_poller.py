import os
import time

from dotenv import load_dotenv

from danny_checksum.connectors.chat_programs.slack_client import SlackClient
from danny_checksum.connectors.database.slack_dao import get_last_thread_ts, set_last_thread_ts

CHANNEL_ID = "C0AFX0Y4U1M"


def poll_slack_channel(client: SlackClient, channel_id: str) -> None:
    client.join_channel(channel_id)
    result = client.client.conversations_history(channel=channel_id, limit=1)
    messages = result.get("messages", [])
    if not messages:
        return

    latest_ts = messages[0]["ts"]
    previous_ts = get_last_thread_ts(channel_id)

    if previous_ts is None:
        print(f"Slack poller: initializing channel {channel_id} at ts={latest_ts}")
        set_last_thread_ts(channel_id, latest_ts)
    elif previous_ts != latest_ts:
        print(f"Slack poller: new thread detected in {channel_id}! {previous_ts} -> {latest_ts}")
        set_last_thread_ts(channel_id, latest_ts)


if __name__ == "__main__":
    load_dotenv()
    client = SlackClient.from_token(os.environ["SLACK_AUTH_TOKEN"])
    print(f"Polling #{CHANNEL_ID} every 10s...")
    while True:
        try:
            poll_slack_channel(client, CHANNEL_ID)
        except Exception as e:
            print(f"poll_slack_channel error: {e}")
        time.sleep(10)
