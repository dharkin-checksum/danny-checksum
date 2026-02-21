import asyncio
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Query
from pydantic import BaseModel

from danny_checksum.business_logic.classical.backend.pollers.git_poller import poll_main_branch
from danny_checksum.business_logic.classical.backend.pollers.slack_poller import poll_slack_channel
from danny_checksum.connectors.chat_programs.slack_client import SlackClient
from danny_checksum.connectors.database import deployment_dao
from danny_checksum.connectors.source_control.github_client import GitHubClient

client: GitHubClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    load_dotenv()
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPO"]
    client = GitHubClient.from_token(token)

    slack_token = os.environ["SLACK_AUTH_TOKEN"]
    slack_channel_id = "C0AFX0Y4U1M"
    slack_client = SlackClient.from_token(slack_token)

    async def _poll_git():
        while True:
            try:
                poll_main_branch(client, repo)
            except Exception as e:
                print(f"poll_main_branch error: {e}")
            await asyncio.sleep(300)

    async def _poll_slack():
        while True:
            try:
                poll_slack_channel(slack_client, slack_channel_id)
            except Exception as e:
                print(f"poll_slack_channel error: {e}")
            await asyncio.sleep(300)

    git_task = asyncio.create_task(_poll_git())
    slack_task = asyncio.create_task(_poll_slack())
    yield
    git_task.cancel()
    slack_task.cancel()


app = FastAPI(title="Danny Checksum GitHub API", lifespan=lifespan)


# --- Request models ---


class CreateIssueRequest(BaseModel):
    repo: str
    title: str
    body: str = ""


class CommentOnIssueRequest(BaseModel):
    repo: str
    issue_number: int
    body: str


class CreatePullRequestRequest(BaseModel):
    repo: str
    title: str
    body: str
    head: str
    base: str = "main"


class CommentOnPrRequest(BaseModel):
    repo: str
    pr_number: int
    body: str


class CreateOrUpdateFileRequest(BaseModel):
    repo: str
    path: str
    content: str
    message: str
    branch: str = "main"


class DeploymentRequest(BaseModel):
    component: str
    sha: str


# --- Deployments ---


@app.post("/deployment")
def create_deployment(req: DeploymentRequest):
    deployment_dao.create_deployment(req.component, req.sha)
    return {"result": "ok"}


# --- Issues ---


@app.get("/issues")
def list_issues(repo: str, state: str = Query("open")):
    return {"result": client.list_issues(repo, state)}


@app.get("/issues/{issue_number}")
def get_issue(issue_number: int, repo: str):
    return {"result": client.get_issue(repo, issue_number)}


@app.post("/issues")
def create_issue(req: CreateIssueRequest):
    return {"result": client.create_issue(req.repo, req.title, req.body)}


@app.post("/issues/{issue_number}/comments")
def comment_on_issue(issue_number: int, req: CommentOnIssueRequest):
    return {"result": client.comment_on_issue(req.repo, issue_number, req.body)}


# --- Pull Requests ---


@app.get("/pulls")
def list_pull_requests(repo: str, state: str = Query("open")):
    return {"result": client.list_pull_requests(repo, state)}


@app.get("/pulls/{pr_number}")
def get_pull_request(pr_number: int, repo: str):
    return {"result": client.get_pull_request(repo, pr_number)}


@app.post("/pulls")
def create_pull_request(req: CreatePullRequestRequest):
    return {"result": client.create_pull_request(req.repo, req.title, req.body, req.head, req.base)}


@app.post("/pulls/{pr_number}/comments")
def comment_on_pr(pr_number: int, req: CommentOnPrRequest):
    return {"result": client.comment_on_pr(req.repo, pr_number, req.body)}


# --- Repo Content ---


@app.get("/repos/file")
def get_file_content(repo: str, path: str, ref: str = Query("main")):
    return {"result": client.get_file_content(repo, path, ref)}


@app.get("/repos/directory")
def list_directory(repo: str, path: str = Query("")):
    return {"result": client.list_directory(repo, path)}


@app.post("/repos/file")
def create_or_update_file(req: CreateOrUpdateFileRequest):
    return {"result": client.create_or_update_file(req.repo, req.path, req.content, req.message, req.branch)}
