import os
from typing import Dict, Any, List
from google import genai

class AIEngine:
    """Generates AI-powered remediation advice for static analysis security findings."""

    @staticmethod
    def analyze_findings(file_path: str, code_snippet: str, security_issues: List[Dict[str, Any]]) -> str:
        if not security_issues:
            return "No critical security vulnerabilities detected."

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return (
                f"**Security Risk Detected in `{file_path}`**:\n"
                f"- Issues: {len(security_issues)} static analysis finding(s).\n"
                f"- Note: GEMINI_API_KEY environment variable not set. Running in fallback mode.\n"
                f"- Verdict: **BLOCK PR**"
            )

        prompt = (
            f"You are an expert DevSecOps Security Engineer reviewing a Pull Request.\n\n"
            f"File: {file_path}\n"
            f"Code Snippet:\n{code_snippet}\n\n"
            f"Flagged Security Findings:\n{security_issues}\n\n"
            f"Provide a concise review summary:\n"
            f"1. Explain the security risk in plain terms.\n"
            f"2. Provide the corrected, secure Python code snippet.\n"
            f"3. Classify the priority (Block PR / Advisory)."
        )

        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"AI Engine Error: Failed to generate response ({str(e)})"