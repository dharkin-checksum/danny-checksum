import asyncio

from crontab import CronTab

from danny_checksum.connectors.source_control.github_client import GitHubClient

_last_sha: str | None = None

CronTab("*/5 * * * *")
def poll_main_branch(client: GitHubClient, repo: str) -> None:
    global _last_sha
    branch = client.github.get_repo(repo).get_branch("main")
    current_sha = branch.commit.sha
    if _last_sha is not None and current_sha != _last_sha:
        print("repo changed!")
    _last_sha = current_sha
