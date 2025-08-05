import os
import re
import json
import hashlib
import requests
import pandas as pd
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

PROCESSED_PAGES_FILE = "processed_confluence_pages.json"

def load_processed_pages():
    if os.path.exists(PROCESSED_PAGES_FILE):
        try:
            with open(PROCESSED_PAGES_FILE, "r") as f:
                data = f.read().strip()
                return set(json.loads(data)) if data else set()
        except Exception as e:
            print(f"Warning: Could not load processed pages file: {e}")
    return set()

def save_processed_pages(processed_pages):
    with open(PROCESSED_PAGES_FILE, "w") as f:
        json.dump(list(processed_pages), f)

with open("config.json", "r") as f:
    DOMAIN_CONFIG = json.load(f)

def generate_test_cases(document_text, api_key, output_excel_path):
    prompt = f"""
You are a highly experienced QA Engineer. Analyze the provided document and generate 30–40 scenario-based test cases.

Include:
- Scenario
- TestCaseID
- Description
- Steps
- ExpectedResult

Document:
---
{document_text}
---"""
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "Scenario": {"type": "STRING"},
                        "TestCaseID": {"type": "STRING"},
                        "Description": {"type": "STRING"},
                        "Steps": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "ExpectedResult": {"type": "STRING"}
                    },
                    "required": ["Scenario", "TestCaseID", "Description", "Steps", "ExpectedResult"]
                }
            }
        }
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    response = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
    response.raise_for_status()
    content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    df = pd.DataFrame(json.loads(content))
    df['Steps'] = df['Steps'].apply(lambda steps: "\n".join(steps) if isinstance(steps, list) else steps)
    df.to_excel(output_excel_path, index=False)
    return output_excel_path

def send_slack_notification(message, config):
    payload = {"text": message}
    requests.post(config["SLACK_WEBHOOK_URL"], json=payload)


def automate_specific_sprint_by_id(board_name_input, sprint_id_input):
    processed = load_processed_pages()
    updated = False

    for domain, config in DOMAIN_CONFIG.items():
        auth = HTTPBasicAuth(config["JIRA_EMAIL"], config["JIRA_API_TOKEN"])
        GEMINI_API_KEY = config["GEMINI_API_KEY"]
        JIRA_BASE = config["JIRA_BASE"]
        CONFLUENCE_BASE = config["CONFLUENCE_BASE"]

        try:
            boards_url = f"{JIRA_BASE}/rest/agile/1.0/board"
            boards = requests.get(boards_url, auth=auth).json().get("values", [])
            print("[DEBUG] Boards fetched from Jira:")
            for b in boards:
                print(f"  - '{b['name']}'")
            board = next((b for b in boards if b["name"].lower() == board_name_input.lower()), None)
            if not board:
                print(f"[DEBUG] Board '{board_name_input}' not found in Jira boards.")
                continue

            board_id = board["id"]
            
            # Fetching sprint details by ID
            sprint_url = f"{JIRA_BASE}/rest/agile/1.0/sprint/{sprint_id_input}"
            sprint_resp = requests.get(sprint_url, auth=auth)
            if sprint_resp.status_code != 200:
                print(f"[DEBUG] Sprint ID '{sprint_id_input}' not found in Jira.")
                continue
            sprint = sprint_resp.json()
            sprint_name = sprint.get("name", f"sprint_{sprint_id_input}")

            #  Extracting test cases from Confluence doc in goal section
            goal = sprint.get("goal", "")
            match = re.search(r"https://[^\s]+/wiki[^\s]*", goal)
            if match:
                confluence_url = match.group()
                page_id_match = re.search(r"/(\d+)", confluence_url)
                if page_id_match:
                    page_id = page_id_match.group(1)
                    if page_id not in processed:
                        domain_match = re.search(r"https://([a-zA-Z0-9\-]+)\.atlassian\.net", confluence_url)
                        if domain_match:
                            conf_domain = domain_match.group(1) + ".atlassian.net"
                            if conf_domain in DOMAIN_CONFIG:
                                conf_config = DOMAIN_CONFIG[conf_domain]
                                conf_auth = HTTPBasicAuth(conf_config["JIRA_EMAIL"], conf_config["JIRA_API_TOKEN"])
                                conf_base = conf_config["CONFLUENCE_BASE"]

                                response = requests.get(
                                    f"{conf_base}/rest/api/content/{page_id}?expand=body.storage",
                                    auth=conf_auth,
                                    headers={"Accept": "application/json"}
                                )
                                response.raise_for_status()
                                html = response.json()["body"]["storage"]["value"]
                                text = BeautifulSoup(html, "html.parser").get_text()
                                filename = f"{sprint_name.replace(' ', '_')}_confluence_testcases.xlsx"
                                generate_test_cases(text, GEMINI_API_KEY, filename)

                                issues = requests.get(f"{JIRA_BASE}/rest/agile/1.0/sprint/{sprint_id_input}/issue", auth=auth).json().get("issues", [])
                                for issue in issues:
                                    key = issue["key"]
                                    with open(filename, "rb") as f:
                                        requests.post(
                                            f"{JIRA_BASE}/rest/api/3/issue/{key}/attachments",
                                            files={"file": (filename, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                                            headers={"X-Atlassian-Token": "no-check"},
                                            auth=auth
                                        )
                                    send_slack_notification(f"✅ Confluence test cases attached to *{key}* in *{sprint_name}*", config)
                                processed.add(page_id)
                                updated = True

         # Extracting test cases from each issue (summary, description, txt files)
            issues = requests.get(f"{JIRA_BASE}/rest/agile/1.0/sprint/{sprint_id_input}/issue", auth=auth).json().get("issues", [])
            for issue in issues:
                key = issue["key"]
                fields = issue.get("fields", {})
                master_text = []

                if fields.get("summary"):
                    master_text.append("Summary:\n" + fields["summary"])
                if fields.get("description"):
                    master_text.append("Description:\n" + fields["description"])
                for att in fields.get("attachment", []):
                    if att["filename"].endswith(".txt"):
                        txt_data = requests.get(att["content"], auth=auth).text
                        master_text.append(f"Attachment ({att['filename']}):\n{txt_data}")

                if master_text:
                    combined = "\n\n".join(master_text)
                    hashval = hashlib.sha256(combined.encode()).hexdigest()
                    if hashval not in processed:
                        filename = f"{key}_issue_testcases.xlsx"
                        generate_test_cases(combined, GEMINI_API_KEY, filename)
                        with open(filename, "rb") as f:
                            requests.post(
                                f"{JIRA_BASE}/rest/api/3/issue/{key}/attachments",
                                files={"file": (filename, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                                headers={"X-Atlassian-Token": "no-check"},
                                auth=auth
                            )
                        send_slack_notification(f"🧪 Test cases generated from issue *{key}* and attached.", config)
                        processed.add(hashval)
                        updated = True

        except Exception as e:
            send_slack_notification(f"❌ Error in sprint ID *{sprint_id_input}* on board *{board_name_input}*: {str(e)}", config)

    if updated:
        save_processed_pages(processed)

if __name__ == "__main__":
    print("🔷 Enter the Sprint Board Name:", end=" ")
    board_input = input().strip()
    print("🟢 Enter the Sprint ID: ", end=" ")
    sprint_id_input = input().strip()
    automate_specific_sprint_by_id(board_input, sprint_id_input)
