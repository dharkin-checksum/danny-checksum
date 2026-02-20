from dataclasses import dataclass

from github import Auth, Github


@dataclass
class GitHubClient:
    github: Github

    @classmethod
    def from_token(cls, token: str) -> "GitHubClient":
        return cls(github=Github(auth=Auth.Token(token)))
