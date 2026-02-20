from dataclasses import dataclass

from github import Auth, Github


@dataclass
class GitHubClient:
    github: Github

    @classmethod
    def from_token(cls, token: str) -> "GitHubClient":
        return cls(github=Github(auth=Auth.Token(token)))

    # --- Issues ---

    def list_issues(self, repo: str, state: str = "open") -> str:
        issues = self.github.get_repo(repo).get_issues(state=state)
        lines = []
        count = 0
        for issue in issues:
            if count >= 25:
                break
            if issue.pull_request is None:
                lines.append(f"#{issue.number} [{issue.state}] {issue.title}")
                count += 1
        return "\n".join(lines) if lines else "No issues found."

    def get_issue(self, repo: str, issue_number: int) -> str:
        issue = self.github.get_repo(repo).get_issue(issue_number)
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

    def create_issue(self, repo: str, title: str, body: str = "") -> str:
        issue = self.github.get_repo(repo).create_issue(title=title, body=body)
        return f"Created issue #{issue.number}: {issue.html_url}"

    def comment_on_issue(self, repo: str, issue_number: int, body: str) -> str:
        issue = self.github.get_repo(repo).get_issue(issue_number)
        comment = issue.create_comment(body=body)
        return f"Comment added: {comment.html_url}"

    # --- Pull Requests ---

    def list_pull_requests(self, repo: str, state: str = "open") -> str:
        prs = self.github.get_repo(repo).get_pulls(state=state)
        lines = []
        for i, pr in enumerate(prs):
            if i >= 25:
                break
            lines.append(f"#{pr.number} [{pr.state}] {pr.title}")
        return "\n".join(lines) if lines else "No pull requests found."

    def get_pull_request(self, repo: str, pr_number: int) -> str:
        pr = self.github.get_repo(repo).get_pull(pr_number)
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

    def create_pull_request(
        self, repo: str, title: str, body: str, head: str, base: str = "main"
    ) -> str:
        pr = self.github.get_repo(repo).create_pull(
            title=title, body=body, head=head, base=base
        )
        return f"Created PR #{pr.number}: {pr.html_url}"

    def comment_on_pr(self, repo: str, pr_number: int, body: str) -> str:
        pr = self.github.get_repo(repo).get_pull(pr_number)
        comment = pr.create_issue_comment(body=body)
        return f"Comment added: {comment.html_url}"

    # --- Repo Content ---

    def get_file_content(self, repo: str, path: str, ref: str = "main") -> str:
        content = self.github.get_repo(repo).get_contents(path, ref=ref)
        if isinstance(content, list):
            return "Error: path is a directory, not a file. Use list_directory instead."
        return content.decoded_content.decode()

    def list_directory(self, repo: str, path: str = "") -> str:
        contents = self.github.get_repo(repo).get_contents(path)
        if not isinstance(contents, list):
            return f"{contents.path} (file, {contents.size} bytes)"
        lines = []
        for item in contents:
            kind = "dir" if item.type == "dir" else "file"
            lines.append(f"[{kind}] {item.path}")
        return "\n".join(lines) if lines else "Empty directory."

    def create_or_update_file(
        self, repo: str, path: str, content: str, message: str, branch: str = "main"
    ) -> str:
        r = self.github.get_repo(repo)
        try:
            existing = r.get_contents(path, ref=branch)
            if isinstance(existing, list):
                return "Error: path is a directory."
            r.update_file(path, message, content, existing.sha, branch=branch)
            return f"Updated {path} on {branch}."
        except Exception:
            r.create_file(path, message, content, branch=branch)
            return f"Created {path} on {branch}."
