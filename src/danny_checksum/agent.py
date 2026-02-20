from pydantic_ai import Agent, RunContext

from danny_checksum.github_client import GitHubClient

agent = Agent(
    "anthropic:claude-sonnet-4-6",
    deps_type=GitHubClient,
    instructions=(
        "You are a helpful GitHub assistant. You can read and write issues, "
        "pull requests, and repository content. When the user refers to a repo, "
        "they mean a GitHub repository in 'owner/repo' format."
    ),
)


# --- Issues ---


@agent.tool
def list_issues(
    ctx: RunContext[GitHubClient], repo: str, state: str = "open"
) -> str:
    """List issues in a GitHub repository.

    Args:
        repo: Repository in 'owner/repo' format.
        state: Issue state: 'open', 'closed', or 'all'.
    """
    issues = ctx.deps.github.get_repo(repo).get_issues(state=state)
    lines = []
    count = 0
    for issue in issues:
        if count >= 25:
            break
        if issue.pull_request is None:
            lines.append(f"#{issue.number} [{issue.state}] {issue.title}")
            count += 1
    return "\n".join(lines) if lines else "No issues found."


@agent.tool
def get_issue(ctx: RunContext[GitHubClient], repo: str, issue_number: int) -> str:
    """Get details of a specific issue.

    Args:
        repo: Repository in 'owner/repo' format.
        issue_number: The issue number.
    """
    issue = ctx.deps.github.get_repo(repo).get_issue(issue_number)
    parts = [
        f"#{issue.number} [{issue.state}] {issue.title}",
        f"Author: {issue.user.login}",
        f"Created: {issue.created_at}",
        f"Labels: {', '.join(l.name for l in issue.labels) or 'none'}",
        "",
        issue.body or "(no body)",
    ]
    comments = issue.get_comments()
    if comments.totalCount > 0:
        parts.append(f"\n--- Comments ({comments.totalCount}) ---")
        for i, c in enumerate(comments):
            if i >= 10:
                break
            parts.append(f"\n{c.user.login} ({c.created_at}):\n{c.body}")
    return "\n".join(parts)


@agent.tool
def create_issue(
    ctx: RunContext[GitHubClient], repo: str, title: str, body: str = ""
) -> str:
    """Create a new issue in a repository.

    Args:
        repo: Repository in 'owner/repo' format.
        title: Issue title.
        body: Issue body (markdown).
    """
    issue = ctx.deps.github.get_repo(repo).create_issue(title=title, body=body)
    return f"Created issue #{issue.number}: {issue.html_url}"


@agent.tool
def comment_on_issue(
    ctx: RunContext[GitHubClient], repo: str, issue_number: int, body: str
) -> str:
    """Add a comment to an issue.

    Args:
        repo: Repository in 'owner/repo' format.
        issue_number: The issue number.
        body: Comment body (markdown).
    """
    issue = ctx.deps.github.get_repo(repo).get_issue(issue_number)
    comment = issue.create_comment(body=body)
    return f"Comment added: {comment.html_url}"


# --- Pull Requests ---


@agent.tool
def list_pull_requests(
    ctx: RunContext[GitHubClient], repo: str, state: str = "open"
) -> str:
    """List pull requests in a repository.

    Args:
        repo: Repository in 'owner/repo' format.
        state: PR state: 'open', 'closed', or 'all'.
    """
    prs = ctx.deps.github.get_repo(repo).get_pulls(state=state)
    lines = []
    for i, pr in enumerate(prs):
        if i >= 25:
            break
        lines.append(f"#{pr.number} [{pr.state}] {pr.title}")
    return "\n".join(lines) if lines else "No pull requests found."


@agent.tool
def get_pull_request(
    ctx: RunContext[GitHubClient], repo: str, pr_number: int
) -> str:
    """Get details of a specific pull request.

    Args:
        repo: Repository in 'owner/repo' format.
        pr_number: The PR number.
    """
    pr = ctx.deps.github.get_repo(repo).get_pull(pr_number)
    parts = [
        f"#{pr.number} [{pr.state}] {pr.title}",
        f"Author: {pr.user.login}",
        f"Branch: {pr.head.ref} -> {pr.base.ref}",
        f"Created: {pr.created_at}",
        f"Mergeable: {pr.mergeable}",
        "",
        pr.body or "(no body)",
    ]
    return "\n".join(parts)


@agent.tool
def create_pull_request(
    ctx: RunContext[GitHubClient],
    repo: str,
    title: str,
    body: str,
    head: str,
    base: str = "main",
) -> str:
    """Create a new pull request.

    Args:
        repo: Repository in 'owner/repo' format.
        title: PR title.
        body: PR description (markdown).
        head: The branch containing changes.
        base: The branch to merge into (default: main).
    """
    pr = ctx.deps.github.get_repo(repo).create_pull(
        title=title, body=body, head=head, base=base
    )
    return f"Created PR #{pr.number}: {pr.html_url}"


@agent.tool
def comment_on_pr(
    ctx: RunContext[GitHubClient], repo: str, pr_number: int, body: str
) -> str:
    """Add a comment to a pull request.

    Args:
        repo: Repository in 'owner/repo' format.
        pr_number: The PR number.
        body: Comment body (markdown).
    """
    pr = ctx.deps.github.get_repo(repo).get_pull(pr_number)
    comment = pr.create_issue_comment(body=body)
    return f"Comment added: {comment.html_url}"


# --- Repo Content ---


@agent.tool
def get_file_content(
    ctx: RunContext[GitHubClient], repo: str, path: str, ref: str = "main"
) -> str:
    """Read a file from a repository.

    Args:
        repo: Repository in 'owner/repo' format.
        path: File path within the repo.
        ref: Branch or commit ref (default: main).
    """
    content = ctx.deps.github.get_repo(repo).get_contents(path, ref=ref)
    if isinstance(content, list):
        return "Error: path is a directory, not a file. Use list_directory instead."
    return content.decoded_content.decode()


@agent.tool
def list_directory(
    ctx: RunContext[GitHubClient], repo: str, path: str = ""
) -> str:
    """List contents of a directory in a repository.

    Args:
        repo: Repository in 'owner/repo' format.
        path: Directory path (empty string for root).
    """
    contents = ctx.deps.github.get_repo(repo).get_contents(path)
    if not isinstance(contents, list):
        return f"{contents.path} (file, {contents.size} bytes)"
    lines = []
    for item in contents:
        kind = "dir" if item.type == "dir" else "file"
        lines.append(f"[{kind}] {item.path}")
    return "\n".join(lines) if lines else "Empty directory."


@agent.tool
def create_or_update_file(
    ctx: RunContext[GitHubClient],
    repo: str,
    path: str,
    content: str,
    message: str,
    branch: str = "main",
) -> str:
    """Create or update a file in a repository.

    Args:
        repo: Repository in 'owner/repo' format.
        path: File path within the repo.
        content: File content (text).
        message: Commit message.
        branch: Target branch (default: main).
    """
    r = ctx.deps.github.get_repo(repo)
    try:
        existing = r.get_contents(path, ref=branch)
        if isinstance(existing, list):
            return "Error: path is a directory."
        r.update_file(path, message, content, existing.sha, branch=branch)
        return f"Updated {path} on {branch}."
    except Exception:
        r.create_file(path, message, content, branch=branch)
        return f"Created {path} on {branch}."
