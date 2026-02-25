from pydantic_ai import Agent

from danny_checksum.connectors.source_control.github_client import GitHubClient


def create_agent(client: GitHubClient) -> Agent:
    agent = Agent(
        "anthropic:claude-sonnet-4-6",
        instructions=(
            "You are a helpful GitHub assistant. You can read and write issues, "
            "pull requests, and repository content. When the user refers to a repo, "
            "they mean a GitHub repository in 'owner/repo' format."
        ),
    )

    # --- Issues ---

    @agent.tool_plain
    def list_issues(repo: str, state: str = "open") -> str:
        """List issues in a GitHub repository.

        Args:
            repo: Repository in 'owner/repo' format.
            state: Issue state: 'open', 'closed', or 'all'.
        """
        return client.list_issues(repo, state)

    @agent.tool_plain
    def get_issue(repo: str, issue_number: int) -> str:
        """Get details of a specific issue.

        Args:
            repo: Repository in 'owner/repo' format.
            issue_number: The issue number.
        """
        return client.get_issue(repo, issue_number)

    @agent.tool_plain
    def create_issue(repo: str, title: str, body: str = "") -> str:
        """Create a new issue in a repository.

        Args:
            repo: Repository in 'owner/repo' format.
            title: Issue title.
            body: Issue body (markdown).
        """
        return client.create_issue(repo, title, body)

    @agent.tool_plain
    def comment_on_issue(repo: str, issue_number: int, body: str) -> str:
        """Add a comment to an issue.

        Args:
            repo: Repository in 'owner/repo' format.
            issue_number: The issue number.
            body: Comment body (markdown).
        """
        return client.comment_on_issue(repo, issue_number, body)

    # --- Pull Requests ---

    @agent.tool_plain
    def list_pull_requests(repo: str, state: str = "open") -> str:
        """List pull requests in a repository.

        Args:
            repo: Repository in 'owner/repo' format.
            state: PR state: 'open', 'closed', or 'all'.
        """
        return client.list_pull_requests(repo, state)

    @agent.tool_plain
    def get_pull_request(repo: str, pr_number: int) -> str:
        """Get details of a specific pull request.

        Args:
            repo: Repository in 'owner/repo' format.
            pr_number: The PR number.
        """
        return client.get_pull_request(repo, pr_number)

    @agent.tool_plain
    def create_pull_request(
        repo: str, title: str, body: str, head: str, base: str = "main"
    ) -> str:
        """Create a new pull request.

        Args:
            repo: Repository in 'owner/repo' format.
            title: PR title.
            body: PR description (markdown).
            head: The branch containing changes.
            base: The branch to merge into (default: main).
        """
        return client.create_pull_request(repo, title, body, head, base)

    @agent.tool_plain
    def comment_on_pr(repo: str, pr_number: int, body: str) -> str:
        """Add a comment to a pull request.

        Args:
            repo: Repository in 'owner/repo' format.
            pr_number: The PR number.
            body: Comment body (markdown).
        """
        return client.comment_on_pr(repo, pr_number, body)

    # --- Repo Content ---

    @agent.tool_plain
    def get_file_content(repo: str, path: str, ref: str = "main") -> str:
        """Read a file from a repository.

        Args:
            repo: Repository in 'owner/repo' format.
            path: File path within the repo.
            ref: Branch or commit ref (default: main).
        """
        return client.get_file_content(repo, path, ref)

    @agent.tool_plain
    def list_directory(repo: str, path: str = "") -> str:
        """List contents of a directory in a repository.

        Args:
            repo: Repository in 'owner/repo' format.
            path: Directory path (empty string for root).
        """
        return client.list_directory(repo, path)

    @agent.tool_plain
    def create_or_update_file(
        repo: str, path: str, content: str, message: str, branch: str = "main"
    ) -> str:
        """Create or update a file in a repository.

        Args:
            repo: Repository in 'owner/repo' format.
            path: File path within the repo.
            content: File content (text).
            message: Commit message.
            branch: Target branch (default: main).
        """
        return client.create_or_update_file(repo, path, content, message, branch)

    return agent
