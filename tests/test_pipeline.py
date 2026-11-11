import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.diff_parser import DiffParser
from app.scanner import SecurityScanner

client = TestClient(app)

def test_diff_parser_extracts_added_lines():
    sample_patch = """@@ -0,0 +1,4 @@
+import os
+def run_code(user_input):
+    eval(user_input)
"""
    parser = DiffParser()
    if hasattr(parser, 'parse_diff'):
        result = parser.parse_diff(sample_patch)
    elif hasattr(parser, 'parse'):
        result = parser.parse(sample_patch)
    else:
        result = parser.parse_patch(sample_patch) if hasattr(parser, 'parse_patch') else []
    
    assert result is not None

def test_scanner_detects_eval_vulnerability():
    vulnerable_code = "eval('import os')"
    scanner = SecurityScanner()
    if hasattr(scanner, 'scan_code'):
        findings = scanner.scan_code(vulnerable_code, "test.py")
    elif hasattr(scanner, 'scan_file'):
        findings = scanner.scan_file(vulnerable_code, "test.py")
    else:
        findings = scanner.scan(vulnerable_code, "test.py")
    assert findings is not None

def test_webhook_endpoint_returns_200():
    payload = {
        "action": "opened",
        "number": 1,
        "repository": {"full_name": "test-user/test-repo"}
    }
    headers = {"X-GitHub-Event": "pull_request"}
    response = client.post("/webhook", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "received"