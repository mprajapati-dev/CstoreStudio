import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

def check_token_usage():
    client = TestClient(app)
    
    # Query the exposed Prometheus metrics endpoint to find total tokens used
    response = client.get("/metrics")
    metrics_data = response.text
    
    total_tokens = 0.0
    for line in metrics_data.split('\n'):
        if line.startswith("token_usage_total"):
            # Prometheus metrics lines look like: token_usage_total{model="gemini"} 1500.0
            parts = line.split(" ")
            if len(parts) == 2:
                try:
                    total_tokens += float(parts[1])
                except ValueError:
                    pass
                    
    # Let's say our baseline is 5000 tokens for the suite
    BASELINE_TOKENS = int(os.getenv("BASELINE_TOKENS", "5000"))
    max_allowed = BASELINE_TOKENS * 1.20
    
    print(f"--- Cost Tracking Test ---")
    print(f"Calculated Total Tokens Used: {total_tokens}")
    print(f"Current Baseline: {BASELINE_TOKENS}")
    
    github_step_summary = os.getenv("GITHUB_STEP_SUMMARY")
    
    # If token usage is strictly > 20% higher than baseline, show as a warning instead of failing.
    if total_tokens > max_allowed:
        warning_msg = f"Token usage ({total_tokens}) exceeded 20% allowable increase over baseline ({BASELINE_TOKENS}). Max allowed: {max_allowed}"
        print(f"⚠️ WARNING: {warning_msg}")
        
        # This will show up as a bright yellow warning annotation in the GitHub Actions UI
        print(f"::warning title=High Token Cost Detected::{warning_msg}")
        
        if github_step_summary:
            with open(github_step_summary, "a") as f:
                f.write("### ⚠️ Application Cost Warning\n")
                f.write(f"- **Actual Token Usage**: `{total_tokens}` tokens\n")
                f.write(f"- **Expected Baseline**: `{BASELINE_TOKENS}` tokens\n")
                f.write(f"- **Max Allowed (20% tolerance)**: `{max_allowed}` tokens\n\n")
                f.write("> *Cost usage has spiked for this PR. Please review the LLM prompt revisions to ensure we aren't wasting context tokens.* \u200d\n")
    else:
        success_msg = f"Token usage ({total_tokens}) is within acceptable limits."
        print(f"✅ SUCCESS: {success_msg}")
        
        if github_step_summary:
            with open(github_step_summary, "a") as f:
                f.write("### ✅ Cost Tracking Check\n")
                f.write(f"Token usage looks good! Used `{total_tokens}` tokens, safely below the `{max_allowed}` token threshold.\n")

    # Exit 0 so we don't break the build just for going slightly over budget
    sys.exit(0)

if __name__ == "__main__":
    check_token_usage()
