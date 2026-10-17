"""
GitHub REST API integration service for SkillTrace AI.
Provides:
1. Secure account verification and repository retrieval.
2. Official GitHub REST API client with rate limit handling and timeout controls.
3. Strict security filters: excludes credentials, secrets, binary assets, and non-code artifacts.
4. Tree exploration and source file content fetching pinned to commit SHAs.
5. In-memory mock/test client support for isolated unit and integration testing.
"""

from __future__ import annotations
import base64
import os
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import httpx

from ..config import settings

logger = logging.getLogger("skilltrace.github")

GITHUB_API_BASE = "https://api.github.com"

# Sensitive files and path patterns that must NEVER be fetched or retained
SENSITIVE_PATTERNS = [
    r"(^|/)\.env(\..+)?$",
    r"(^|/)(id_rsa|id_dsa|id_ed25519)(\.pub)?$",
    r".*\.(pem|key|pfx|p12|pkcs12|keystore)$",
    r".*(secret|credential|password|token).*\.(json|yml|yaml|txt|conf)$",
    r"(^|/)aws_credentials$",
    r"(^|/)\.git/",
    r"(^|/)node_modules/",
    r"(^|/)\.venv/",
    r"(^|/)venv/",
    r"(^|/)__pycache__/",
    r"(^|/)dist/",
    r"(^|/)build/",
]

# Supported source file extensions for AST and static analysis
SUPPORTED_EXTENSIONS = {
    ".py", ".sql", ".js", ".jsx", ".ts", ".tsx",
    ".json", ".yaml", ".yml", ".md", ".toml", ".txt"
}

SUPPORTED_CONFIG_FILES = {
    "dockerfile", "makefile", "requirements.txt", "pyproject.toml",
    "package.json", "setup.py", "gemfile"
}


class GitHubRateLimitError(Exception):
    """Raised when GitHub API rate limit is exceeded."""
    def __init__(self, message: str, reset_timestamp: Optional[int] = None):
        super().__init__(message)
        self.reset_timestamp = reset_timestamp


class GitHubService:
    def __init__(self):
        self._mock_repos: Dict[str, Dict[str, Any]] = {}

    def is_sensitive_path(self, path: str) -> bool:
        normalized = path.replace("\\", "/").lower()
        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, normalized):
                return True
        return False

    def is_scannable_file(self, path: str, size: int = 0) -> bool:
        if size > settings.MAX_CODE_FILE_SIZE_BYTES:
            return False
        if self.is_sensitive_path(path):
            return False

        normalized = path.replace("\\", "/").lower()
        basename = os.path.basename(normalized)
        _, ext = os.path.splitext(normalized)

        if ext in SUPPORTED_EXTENSIONS or basename in SUPPORTED_CONFIG_FILES:
            return True
        return False

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        auth_token = token or settings.GITHUB_TOKEN
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "SkillTrace-AI-Career-Coach"
        }
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        return headers

    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify GitHub token and retrieve authenticated user profile."""
        if token.startswith("mock_token_"):
            return {
                "id": 1234567,
                "login": token.replace("mock_token_", ""),
                "avatar_url": "https://avatars.githubusercontent.com/u/1234567",
                "html_url": f"https://github.com/{token.replace('mock_token_', '')}",
                "name": "Alex Morgan"
            }

        headers = self._get_headers(token)
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{GITHUB_API_BASE}/user", headers=headers)
            if resp.status_code == 401:
                raise ValueError("Invalid GitHub access token or unauthorized.")
            if resp.status_code == 403 and "rate limit" in resp.text.lower():
                reset_time = int(resp.headers.get("x-ratelimit-reset", 0))
                raise GitHubRateLimitError("GitHub API rate limit exceeded.", reset_time)
            resp.raise_for_status()
            return resp.json()

    async def list_repositories(self, token: Optional[str] = None) -> List[Dict[str, Any]]:
        """List repositories accessible to the user."""
        auth_token = token or settings.GITHUB_TOKEN
        if auth_token and auth_token.startswith("mock_token_"):
            username = auth_token.replace("mock_token_", "")
            return [
                {
                    "id": f"repo-{username}-lab",
                    "full_name": f"{username}/data-pipeline-lab",
                    "name": "data-pipeline-lab",
                    "default_branch": "main",
                    "private": False,
                    "html_url": f"https://github.com/{username}/data-pipeline-lab"
                }
            ]

        headers = self._get_headers(token)
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{GITHUB_API_BASE}/user/repos?per_page=100&sort=updated",
                headers=headers
            )
            if resp.status_code == 403 and "rate limit" in resp.text.lower():
                reset_time = int(resp.headers.get("x-ratelimit-reset", 0))
                raise GitHubRateLimitError("GitHub API rate limit exceeded.", reset_time)
            resp.raise_for_status()
            return resp.json()

    async def get_latest_commit(
        self,
        repo_full_name: str,
        branch: Optional[str] = None,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch latest commit for a repository."""
        if repo_full_name in self._mock_repos:
            mock = self._mock_repos[repo_full_name]
            return {
                "sha": mock.get("commit_sha", "c4a89f2d1e7b"),
                "commit": {
                    "message": "Update data pipeline scripts",
                    "author": {"name": "Alex Morgan", "date": datetime.now(timezone.utc).isoformat()}
                }
            }

        headers = self._get_headers(token)
        url = f"{GITHUB_API_BASE}/repos/{repo_full_name}/commits"
        params = {"per_page": 1}
        if branch:
            params["sha"] = branch

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            commits = resp.json()
            if not commits:
                raise ValueError(f"No commits found for repository {repo_full_name}")
            return commits[0]

    async def get_commit_details(
        self,
        repo_full_name: str,
        commit_sha: str,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch detailed commit info including files added, modified, removed."""
        if repo_full_name in self._mock_repos:
            mock = self._mock_repos[repo_full_name]
            return {
                "sha": commit_sha,
                "commit": {"message": "Mock commit update"},
                "files": mock.get("changed_files", [])
            }

        headers = self._get_headers(token)
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                f"{GITHUB_API_BASE}/repos/{repo_full_name}/commits/{commit_sha}",
                headers=headers
            )
            resp.raise_for_status()
            return resp.json()

    async def fetch_repo_tree(
        self,
        repo_full_name: str,
        commit_sha: str,
        token: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch git tree recursively for a given commit SHA."""
        if repo_full_name in self._mock_repos:
            files = self._mock_repos[repo_full_name].get("files", [])
            return [{"path": f["path"], "type": "blob", "size": len(f["content"])} for f in files]

        headers = self._get_headers(token)
        url = f"{GITHUB_API_BASE}/repos/{repo_full_name}/git/trees/{commit_sha}?recursive=1"
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data.get("tree", [])

    async def fetch_file_content(
        self,
        repo_full_name: str,
        file_path: str,
        commit_sha: str,
        token: Optional[str] = None
    ) -> Optional[str]:
        """Fetch file content decoded from Base64 while enforcing security boundaries."""
        if self.is_sensitive_path(file_path):
            logger.warning(f"Prevented reading sensitive file: {file_path}")
            return None

        if repo_full_name in self._mock_repos:
            files = self._mock_repos[repo_full_name].get("files", [])
            for f in files:
                if f["path"] == file_path:
                    return f["content"]
            return None

        headers = self._get_headers(token)
        url = f"{GITHUB_API_BASE}/repos/{repo_full_name}/contents/{file_path}?ref={commit_sha}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            file_meta = resp.json()
            if file_meta.get("encoding") == "base64" and "content" in file_meta:
                raw_bytes = base64.b64decode(file_meta["content"])
                return raw_bytes.decode("utf-8", errors="replace")
            return None

    async def fetch_scannable_files(
        self,
        repo_full_name: str,
        commit_sha: str,
        token: Optional[str] = None,
        max_files: int = 40
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all valid scannable source files for a repository pinned to commit_sha.
        Never retrieves credentials, secrets, or binary artifacts.
        """
        if repo_full_name in self._mock_repos:
            return list(self._mock_repos[repo_full_name].get("files", []))

        tree_items = await self.fetch_repo_tree(repo_full_name, commit_sha, token)
        scannable = []
        for item in tree_items:
            if item.get("type") != "blob":
                continue
            path = item.get("path", "")
            size = item.get("size", 0)
            if self.is_scannable_file(path, size):
                scannable.append(item)

        # Limit to max_files to respect rate limits
        scannable = scannable[:max_files]
        retrieved_files = []
        for item in scannable:
            path = item["path"]
            content = await self.fetch_file_content(repo_full_name, path, commit_sha, token)
            if content is not None:
                retrieved_files.append({"path": path, "content": content})

        return retrieved_files

    def register_mock_repository(
        self,
        repo_full_name: str,
        commit_sha: str,
        files: List[Dict[str, Any]],
        changed_files: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """Register a mock repository for offline tests or unit testing."""
        self._mock_repos[repo_full_name] = {
            "commit_sha": commit_sha,
            "files": files,
            "changed_files": changed_files or []
        }

    def clear_mocks(self) -> None:
        self._mock_repos.clear()


github_service = GitHubService()
