import os
PROCESSED_PAGES_FILE = "processed_confluence_pages.json"
def load_processed_pages():
    if os.path.exists(PROCESSED_PAGES_FILE):
        try:
            with open(PROCESSED_PAGES_FILE, "r") as f:
                data = f.read().strip()
                if not data:
                    return set()
                return set(json.loads(data))
        except Exception as e:
            print(f"Warning: Could not load processed pages file: {e}. Resetting.")
            return set()
    return set()

def save_processed_pages(processed_pages):
    with open(PROCESSED_PAGES_FILE, "w") as f:
        json.dump(list(processed_pages), f)
import re
import json
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup

# ---------------- CONFIGURATION ---------------- #




# --- DOMAIN CONFIGURATION --- #
with open("config.json", "r") as f:
    DOMAIN_CONFIG = json.load(f)
GEMINI_API_KEY = "AIzaSyB-nLJBAr7sA4mKruorelCMAwcPaorV9zI"

# ------------------------------------------------ #

# ------------------------------------------------ #



def get_domain_config_from_url(url):
    match = re.search(r'https://([\w.-]+)\/', url)
    if not match:
        raise ValueError(f"Could not extract domain from URL: {url}")
    domain = match.group(1)
    config = DOMAIN_CONFIG.get(domain)
    if not config:
        raise ValueError(f"No config found for domain: {domain}")
    return config


def get_all_boards_for_domain(config):
    AUTH = HTTPBasicAuth(config["JIRA_EMAIL"], config["JIRA_API_TOKEN"])
    url = f"{config['JIRA_BASE']}/rest/agile/1.0/board"
    boards = []
    start_at = 0
    while True:
        response = requests.get(f"{url}?startAt={start_at}", auth=AUTH)
        response.raise_for_status()
        data = response.json()
        boards.extend(data["values"])
        if data["isLast"]:
            break
        start_at += data["maxResults"]
    return boards


def get_active_sprints_across_all_domains():
    active_sprints = []
    for domain, config in DOMAIN_CONFIG.items():
        boards = get_all_boards_for_domain(config)
        AUTH = HTTPBasicAuth(config["JIRA_EMAIL"], config["JIRA_API_TOKEN"])
        for board in boards:
            board_id = board["id"]
            board_name = board["name"]
            try:
                url = f"{config['JIRA_BASE']}/rest/agile/1.0/board/{board_id}/sprint?state=active"
                response = requests.get(url, auth=AUTH)
                response.raise_for_status()
                sprints = response.json().get("values", [])
                for sprint in sprints:
                    active_sprints.append({
                        "board_id": board_id,
                        "board_name": board_name,
                        "sprint": sprint,
                        "domain": domain,
                        "config": config
                    })
            except requests.RequestException as e:
                print(f"Failed to fetch sprints for board {board_name} in {domain}: {e}")
    return active_sprints

def get_confluence_page_text(confluence_url):
    config = get_domain_config_from_url(confluence_url)
    AUTH = HTTPBasicAuth(config["JIRA_EMAIL"], config["JIRA_API_TOKEN"])
    CONFLUENCE_BASE = config["CONFLUENCE_BASE"]
    page_id = [part for part in confluence_url.split("/") if part.isdigit()][0]
    response = requests.get(
        f"{CONFLUENCE_BASE}/rest/api/content/{page_id}?expand=body.storage",
        auth=AUTH,
        headers={"Accept": "application/json"}
    )
    response.raise_for_status()
    content = response.json()
    raw_html = content["body"]["storage"]["value"]
    return BeautifulSoup(raw_html, "html.parser").get_text()

def generate_test_cases(document_text, api_key, output_excel_path):
    prompt = f"""
You are a highly experienced QA Engineer. Analyze the provided document and generate 30–40 scenario-based test cases.

Include:
- Scenario
- TestCaseID
- Description
- Steps
- ExpectedResult

Here is the Confluence document text:
---
{document_text}
---
"""
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

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    response = requests.post(api_url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
    response.raise_for_status()
    result = response.json()

    content_parts = result.get("candidates", [])[0]["content"]["parts"]
    json_string = content_parts[0]["text"]
    parsed_test_cases = json.loads(json_string)

    df = pd.DataFrame(parsed_test_cases)
    df['Steps'] = df['Steps'].apply(lambda steps: '\n'.join(steps) if isinstance(steps, list) else steps)
    df.to_excel(output_excel_path, index=False)
    return output_excel_path

def get_issues_in_sprint(sprint_id):
    # This function needs to know which domain to use. For now, use the first config.
    config = list(DOMAIN_CONFIG.values())[0]
    AUTH = HTTPBasicAuth(config["JIRA_EMAIL"], config["JIRA_API_TOKEN"])
    url = f"{config['JIRA_BASE']}/rest/agile/1.0/sprint/{sprint_id}/issue"
    response = requests.get(url, auth=AUTH)
    response.raise_for_status()
    return response.json().get("issues", [])

def attach_file_to_issue(issue_key, file_path):
    # This function needs to know which domain to use. For now, use the first config.
    config = list(DOMAIN_CONFIG.values())[0]
    AUTH = HTTPBasicAuth(config["JIRA_EMAIL"], config["JIRA_API_TOKEN"])
    url = f"{config['JIRA_BASE']}/rest/api/3/issue/{issue_key}/attachments"
    headers = {"X-Atlassian-Token": "no-check"}
    with open(file_path, "rb") as f:
        files = {
            "file": (
                os.path.basename(file_path),
                f,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        }
        response = requests.post(url, headers=headers, auth=AUTH, files=files)
        response.raise_for_status()
        return response.json()

def send_slack_notification(message):
    # Default to first config for notifications (or refactor as needed)
    config = list(DOMAIN_CONFIG.values())[0]
    SLACK_WEBHOOK_URL = config["SLACK_WEBHOOK_URL"]
    payload = {"text": message}
    response = requests.post(
        SLACK_WEBHOOK_URL,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )
    response.raise_for_status()

def automate_all_sprints():

    try:
        active_sprints = get_active_sprints_across_all_domains()
        processed_pages = load_processed_pages()
        updated = False

        if not active_sprints:
            send_slack_notification("⚠️ No active sprints found across all boards.")
            return


        for entry in active_sprints:
            board_id = entry["board_id"]
            board_name = entry["board_name"]
            sprint = entry["sprint"]
            sprint_id = sprint["id"]
            sprint_name = sprint["name"]
            config = entry["config"]

            try:
                goal = sprint.get("goal", "")
                if not goal:
                    print(f"Sprint '{sprint_name}' on board '{board_name}' has no goal. Skipping (no Confluence link).")
                    continue
                match = re.search(r"https://[^\s]+/wiki[^\s]*", goal)
                if not match:
                    print(f"Sprint '{sprint_name}' on board '{board_name}' has no Confluence link in goal. Skipping.")
                    continue

                confluence_link = match.group(0)
                # Extract Confluence page ID (robust for various URL formats)
                page_id_match = re.search(r"/(\d+)(?:/|$)", confluence_link)
                if not page_id_match:
                    print(f"Sprint '{sprint_name}' on board '{board_name}' has a Confluence link but no page ID could be extracted. Skipping.")
                    continue
                page_id = page_id_match.group(1)

                if page_id in processed_pages:
                    print(f"Sprint '{sprint_name}' on board '{board_name}': Test cases already generated for Confluence page {page_id}. Skipping.")
                    continue

                AUTH = HTTPBasicAuth(config["JIRA_EMAIL"], config["JIRA_API_TOKEN"])
                CONFLUENCE_BASE = config["CONFLUENCE_BASE"]
                JIRA_BASE = config["JIRA_BASE"]
                SLACK_WEBHOOK_URL = config["SLACK_WEBHOOK_URL"]

                # Get Confluence page text
                page_id_for_text = [part for part in confluence_link.split("/") if part.isdigit()][0]
                response = requests.get(
                    f"{CONFLUENCE_BASE}/rest/api/content/{page_id_for_text}?expand=body.storage",
                    auth=AUTH,
                    headers={"Accept": "application/json"}
                )
                response.raise_for_status()
                content = response.json()
                raw_html = content["body"]["storage"]["value"]
                document_text = BeautifulSoup(raw_html, "html.parser").get_text()

                filename = f"{board_name.replace(' ', '_')}_{sprint_name.replace(' ', '_')}_testcases.xlsx"
                generate_test_cases(document_text, GEMINI_API_KEY, filename)

                # Use correct config for Jira issue/attachment
                url_issues = f"{JIRA_BASE}/rest/agile/1.0/sprint/{sprint_id}/issue"
                response = requests.get(url_issues, auth=AUTH)
                response.raise_for_status()

                issues = response.json().get("issues", [])
                if issues:
                    attached_issues = []
                    for issue in issues:
                        issue_key = issue["key"]
                        url_attach = f"{JIRA_BASE}/rest/api/3/issue/{issue_key}/attachments"
                        headers = {"X-Atlassian-Token": "no-check"}
                        with open(filename, "rb") as f:
                            files = {
                                "file": (
                                    os.path.basename(filename),
                                    f,
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                            }
                            response_attach = requests.post(url_attach, headers=headers, auth=AUTH, files=files)
                            response_attach.raise_for_status()
                        attached_issues.append(issue_key)
                    send_slack_notification(
                        f"Test cases generated and attached to issues {', '.join(attached_issues)} in *{sprint_name}* (`{board_name}`)."
                    )
                else:
                    print(f"Sprint '{sprint_name}' on board '{board_name}': No issues found. Skipped attachment.")
                    send_slack_notification(
                        f"⚠️ No issues found in *{sprint_name}* (`{board_name}`). Skipped attachment."
                    )

                processed_pages.add(page_id)
                updated = True

            except Exception as e:
                print(f"Sprint '{sprint_name}' on board '{board_name}': Exception occurred: {str(e)}")
                send_slack_notification(
                    f"Failed for *{sprint_name}* on board *{board_name}* ({config['JIRA_BASE']}): {str(e)}"
                )

        if updated:
            save_processed_pages(processed_pages)

    except Exception as e:
        send_slack_notification(f"Automation failed entirely: {str(e)}")



#  ENTRY POINT
if __name__ == "__main__":
    automate_all_sprints()
