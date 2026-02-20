import asyncio

from crontab import CronTab

from danny_checksum.connectors.database.repo_dao import get_last_sha, set_last_sha
from danny_checksum.connectors.source_control.github_client import GitHubClient


CronTab("*/5 * * * *")
def poll_main_branch(client: GitHubClient, repo: str) -> None:
    branch = client.github.get_repo(repo).get_branch("main")
    current_sha = branch.commit.sha

    previous_sha = get_last_sha(repo)
    if previous_sha is not None and previous_sha != current_sha:
        old_blob = client.get_file_blob_sha(repo, ".checksum", ref=previous_sha)
        new_blob = client.get_file_blob_sha(repo, ".checksum", ref=current_sha)
        if old_blob is not None and new_blob is not None and old_blob != new_blob:
            print(f".checksum changed! {previous_sha} -> {current_sha}")
            set_last_sha(repo, current_sha)
