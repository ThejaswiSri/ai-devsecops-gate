import subprocess
import tempfile
import json
import os
from typing import Dict, Any

class SecurityScanner:
    """Runs static analysis security tools (Bandit and Ruff) on code snippets."""

    @staticmethod
    def scan_code(code: str, file_path: str) -> Dict[str, Any]:
        results = {
            "file": file_path,
            "bandit_issues": [],
            "ruff_issues": []
        }

        # Create temporary python file to scan
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name

        try:
            # 1. Run Bandit for security issues
            bandit_cmd = ["bandit", "-f", "json", temp_path]
            bandit_proc = subprocess.run(bandit_cmd, capture_output=True, text=True)
            if bandit_proc.stdout:
                try:
                    bandit_data = json.loads(bandit_proc.stdout)
                    results["bandit_issues"] = bandit_data.get("results", [])
                except json.JSONDecodeError:
                    pass

            # 2. Run Ruff for linting and bugs
            ruff_cmd = ["ruff", "check", "--output-format=json", temp_path]
            ruff_proc = subprocess.run(ruff_cmd, capture_output=True, text=True)
            if ruff_proc.stdout:
                try:
                    results["ruff_issues"] = json.loads(ruff_proc.stdout)
                except json.JSONDecodeError:
                    pass

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        return results