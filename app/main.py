import hmac
import hashlib
from fastapi import FastAPI, Request, HTTPException, Header, BackgroundTasks, status
from app.diff_parser import DiffParser
from app.scanner import SecurityScanner
from app.ai_engine import AIEngine
from app.github_client import GitHubClient

app = FastAPI(
    title="AI DevSecOps Review Gate",
    version="1.0.0"
)

GITHUB_WEBHOOK_SECRET = "my_secret_key"
github_client = GitHubClient()

SAMPLE_DIFF = """diff --git a/app/utils.py b/app/utils.py
index 0000000..1111111 100644
--- a/app/utils.py
+++ b/app/utils.py
@@ -0,0 +1,6 @@
+def execute_user_code(user_input):
+    # Insecure use of eval
+    return eval(user_input)
"""

def verify_signature(payload_body: bytes, signature_header: str):
    if not signature_header:
        raise HTTPException(status_code=403, detail="Missing X-Hub-Signature-256 header")
        
    hash_object = hmac.new(
        GITHUB_WEBHOOK_SECRET.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")

def process_pull_request_event(payload: dict):
    pr_action = payload.get("action")
    pr_number = payload.get("number")
    repo_name = payload.get("repository", {}).get("full_name")
    
    print(f"\n[+] [WORKER] Processing PR #{pr_number} ({pr_action}) for {repo_name}", flush=True)

    # 1. Diff Parsing
    parsed_files = DiffParser.parse_patch(SAMPLE_DIFF)
    print(f"[+] [WORKER] Extracted {len(parsed_files)} Python file(s) from diff.", flush=True)

    # 2. Static Security Scanning
    for f in parsed_files:
        print(f"\n[+] [SCANNER] Scanning file: {f['file_path']}", flush=True)
        scan_results = SecurityScanner.scan_code(f['added_code'], f['file_path'])
        all_issues = scan_results['bandit_issues'] + scan_results['ruff_issues']
        print(f"    - Total Security Findings: {len(all_issues)}", flush=True)

        # 3. AI Security Assessment
        if all_issues:
            print(f"\n[+] [AI ENGINE] Generating remediation assessment...", flush=True)
            ai_review = AIEngine.analyze_findings(f['file_path'], f['added_code'], all_issues)
            print(f"\n--- AI DevSecOps Gate Report ---\n{ai_review}\n--------------------------------", flush=True)

            # 4. Post GitHub Review Comment
            print(f"\n[+] [GITHUB CLIENT] Dispatching review comment to GitHub PR...", flush=True)
            github_client.post_pr_comment(repo_name, pr_number, ai_review)

@app.get("/")
def home():
    return {"message": "AI DevSecOps Review Gate is running!"}

@app.get("/health")
def health_check():
    return {"status": "online", "system": "AI DevSecOps Gate"}

@app.post("/webhook")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    body = await request.body()
    
    if x_github_event == "pull_request":
        payload = await request.json()
        action = payload.get("action")
        background_tasks.add_task(process_pull_request_event, payload)
        
        return {
            "status": "received",
            "event": x_github_event,
            "action": action
        }
        
    return {"status": "ignored", "event": x_github_event}