import os
import time

from dotenv import load_dotenv
from pydantic import TypeAdapter
from pydantic_ai.messages import ModelMessage

from danny_checksum.business_logic.agentic.onboarding_agent import create_agent
from danny_checksum.connectors.chat_programs.slack_client import SlackClient
from danny_checksum.connectors.database import monitored_channel_dao, onboarding_dao, slack_thread_dao
from danny_checksum.connectors.database.slack_dao import get_last_thread_ts, set_last_thread_ts

_message_list_adapter = TypeAdapter(list[ModelMessage])


def poll_slack_channel(
    client: SlackClient, channel_id: str, bot_user_id: str, channel_name: str | None = None
) -> None:
    client.join_channel(channel_id)

    # --- Part 1: new top-level messages ---
    result = client.client.conversations_history(channel=channel_id, limit=5)
    messages = result.get("messages", [])
    if not messages:
        return

    previous_ts = get_last_thread_ts(channel_id)

    for msg in reversed(messages):
        ts = msg["ts"]

        # Only look at messages newer than what we've already processed
        if previous_ts is not None and ts <= previous_ts:
            continue

        # Skip bot's own messages
        if msg.get("user") == bot_user_id:
            continue

        # Skip threaded replies (they have a thread_ts different from their ts)
        if msg.get("thread_ts") and msg["thread_ts"] != ts:
            continue

        # Skip if we already created a thread for this message (crash recovery)
        if slack_thread_dao.get_thread_by_ts(ts) is not None:
            continue

        text = msg.get("text", "")
        print(f"Slack poller: new message in {channel_id}: {text[:80]}")

        # Create onboarding session + slack thread
        session_id = onboarding_dao.create_session(phase="sales")
        slack_thread_dao.create_thread(channel_id, ts, session_id)

        # Run the onboarding agent
        agent = create_agent(role="sales", session_id=session_id, channel_name=channel_name)
        agent_result = agent.run_sync(text)

        # Post the reply in a thread
        reply_data = client.post_message(channel_id, agent_result.output, thread_ts=ts)
        reply_ts = reply_data.get("ts", ts)

        # Persist message history
        history_json = _message_list_adapter.dump_json(agent_result.all_messages()).decode()
        slack_thread_dao.update_message_history(ts, history_json, reply_ts)

    # Update the high-water mark to the latest message ts
    set_last_thread_ts(channel_id, messages[0]["ts"])

    # --- Part 2: existing thread replies ---
    tracked_threads = slack_thread_dao.get_active_threads(channel_id)

    for thread in tracked_threads:
        replies = client.read_thread_replies(
            channel_id, thread.thread_ts, oldest=thread.last_reply_ts
        )

        # Filter out bot messages and already-seen messages
        new_user_replies = [
            r for r in replies
            if r.get("user") != bot_user_id
            and (thread.last_reply_ts is None or r["ts"] > thread.last_reply_ts)
        ]

        if not new_user_replies:
            continue

        # Load existing message history
        if thread.message_history_json:
            history = _message_list_adapter.validate_json(thread.message_history_json)
        else:
            history = []

        # Recreate agent for this session
        agent = create_agent(role="sales", session_id=thread.session_id, channel_name=channel_name)

        # Process each new reply
        latest_reply_ts = thread.last_reply_ts
        for reply in new_user_replies:
            text = reply.get("text", "")
            print(f"Slack poller: thread reply in {thread.thread_ts}: {text[:80]}")

            agent_result = agent.run_sync(text, message_history=history)
            history = agent_result.all_messages()

            reply_data = client.post_message(
                channel_id, agent_result.output, thread_ts=thread.thread_ts
            )
            latest_reply_ts = reply_data.get("ts", reply["ts"])

        # Persist updated history
        history_json = _message_list_adapter.dump_json(history).decode()
        slack_thread_dao.update_message_history(
            thread.thread_ts, history_json, latest_reply_ts
        )


def poll_all_slack_channels(client: SlackClient, bot_user_id: str) -> None:
    """Poll all monitored channels from the database."""
    channels = monitored_channel_dao.list_channels()
    for ch in channels:
        poll_slack_channel(client, ch.channel_id, bot_user_id, ch.name)


if __name__ == "__main__":
    load_dotenv()
    client = SlackClient.from_token(os.environ["SLACK_AUTH_TOKEN"])
    bot_user_id = client.get_bot_user_id()
    print(f"Bot user ID: {bot_user_id}")
    channels = monitored_channel_dao.list_channels()
    print(f"Monitoring {len(channels)} channel(s): {', '.join(f'#{c.name}' for c in channels)}")
    print("Polling every 10s...")
    while True:
        try:
            poll_all_slack_channels(client, bot_user_id)
        except Exception as e:
            print(f"poll_all_slack_channels error: {e}")
        time.sleep(10)
