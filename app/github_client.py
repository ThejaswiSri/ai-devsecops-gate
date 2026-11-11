import httpx
import os
from typing import Dict, Any

class GitHubClient:
    """Handles interactions with the GitHub REST API to post review comments."""

    def __init__(self, token: str = None):
        self.token = token or os.getenv("GITHUB_TOKEN", "")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def post_pr_comment(self, repo_full_name: str, pr_number: int, comment_body: str) -> Dict[str, Any]:
        """Posts a PR review comment to GitHub."""
        if not self.token:
            print("[!] [GITHUB CLIENT] Warning: No GITHUB_TOKEN provided. Simulating comment post locally.", flush=True)
            return {"status": "simulated", "comment": comment_body}

        url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
        payload = {"body": comment_body}

        with httpx.Client() as client:
            response = client.post(url, headers=self.headers, json=payload)
            if response.status_code == 201:
                print(f"[+] [GITHUB CLIENT] Successfully posted review comment to PR #{pr_number}", flush=True)
                return response.json()
            else:
                print(f"[!] [GITHUB CLIENT] Failed to post comment: {response.status_code} - {response.text}", flush=True)
                return {"status": "failed", "code": response.status_code}