# 🧪 Automated Test Case Generator (Jira + Confluence + Gemini + Slack)

This repository contains a powerful Python script that automates the generation of test cases by integrating **Jira**, **Confluence**, **Google Gemini**, and **Slack**.

> ⚡️ It pulls sprint issues and Confluence documents, generates detailed test cases using Gemini AI, attaches them to Jira issues, and posts real-time notifications to Slack.

---

## 🔍 Use Case

This script is ideal for:

- QA teams who want automated, consistent test case generation
- Product & Sprint managers looking to reduce manual documentation
- Teams using Jira & Confluence for agile project tracking
- Fast, one-click test case creation at scale using AI

---

## 📦 Features

- 🔁 **Supports multiple Jira domains** via single config file
- 📥 **Fetches the latest active sprint** based on board/sprint name input
- 📄 Extracts **Confluence content from sprint goal**
- 🧾 Parses **summary, description, and `.txt` attachments** of each issue
- 🤖 Sends prompts to **Gemini AI** to generate 30–40 scenario-based test cases
- 📎 Attaches Excel test cases (`.xlsx`) to respective Jira issues
- 📢 Sends real-time **Slack notifications**
- 🔒 Prevents duplicate generation using content **hashing & history tracking**

---

## 📁 Folder Structure
testCaseAutomation/
│
├── auto_testcase_generator.py # Main script
├── config.json # Stores domain credentials
├── processed_confluence_pages.json # History of processed data
├── README.md # This file
├── requirements.txt # Dependencies


---

## 🛠️ Setup & Installation

1. **Clone this repository**

```bash
git clone https://github.com/<your-username>/testCaseAutomation.git
cd testCaseAutomation


pip install -r requirements.txt


// config.json
{
  "your-domain.atlassian.net": {
    "JIRA_EMAIL": "your_email@example.com",
    "JIRA_API_TOKEN": "your_jira_api_token",
    "JIRA_BASE": "https://your-domain.atlassian.net",
    "CONFLUENCE_BASE": "https://your-domain.atlassian.net/wiki",
    "GEMINI_API_KEY": "your_gemini_api_key",
    "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/XXX/YYY/ZZZ"
  },

  "another-domain.atlassian.net": {
    "JIRA_EMAIL": "another@example.com",
    "JIRA_API_TOKEN": "another_jira_token",
    "JIRA_BASE": "https://another-domain.atlassian.net",
    "CONFLUENCE_BASE": "https://another-domain.atlassian.net/wiki",
    "GEMINI_API_KEY": "another_gemini_key",
    "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/ABC/DEF/GHI"
  }
}

python auto_testcase_generator.py

When prompted:

yaml
Copy
Edit
🔷 Enter the Sprint Board Name: SYMREC
🟢 Enter the Sprint Name: SYMREC Sprint 4
The script will:

Search across all configured domains

Match the board and sprint name

Pull issues and Confluence content

Generate & attach test cases

Post updates to Slack

💡 How It Works (Simplified Flow)
🔎 Get input for board name and sprint name

🌐 Search through all domains to find the matching sprint

📂 Parse issues for summary, description, and .txt attachments

📄 Extract sprint goal Confluence link

🤖 Send prompt to Gemini AI with content

📊 Receive and parse AI response (JSON to Excel)

📎 Attach test cases back to Jira issue

🔔 Send notification to Slack

📌 Skip re-processing already handled data

🛑 Re-run Safety
✅ No duplicates: The script saves hashes of content and page IDs

✅ Re-runs only generate test cases for new/unprocessed items

✅ All processed items are tracked in processed_confluence_pages.json

📬 Slack Notification Samples
✅ Confluence test cases attached to *SYMREC-104* in *SYMREC Sprint 4*

🧪 Test cases generated from issue *SYMREC-105* and attached.

❌ Error in sprint *SYMREC Sprint 4* on board *SYMREC*: [Error Details]

📄 Test Case Format
All generated Excel sheets include:

Scenario	TestCaseID	Description	Steps	ExpectedResult

🔐 Gemini Prompt Example
txt
Copy
Edit
You are a highly experienced QA Engineer. Analyze the provided document and generate 30–40 scenario-based test cases.
Include: Scenario, TestCaseID, Description, Steps, ExpectedResult
🔗 References
Jira REST API

Confluence REST API

Google Gemini API

Slack Incoming Webhooks

🧪 Sample Output Files
SYMREC_Sprint_4_confluence_testcases.xlsx

SYMREC-105_issue_testcases.xlsx

These are automatically created and attached.

📋 Requirements
txt
Copy
Edit
requests
pandas
beautifulsoup4
openpyxl
Install with:

bash
Copy
Edit
pip install -r requirements.txt
🙋 FAQ
Q: Can I run this on multiple domains?
A: Yes! Add multiple entries in your config.json.

Q: What if I run it again for the same sprint?
A: Test cases will only be generated for new or updated issues.

Q: Do I need to manually enter board/sprint every time?
A: Yes, the script takes sprint and board names as input at runtime.

🤝 Contributing
Pull requests are welcome! For bugs or suggestions, open an issue.

📜 License
This project is licensed under the MIT License.

👨‍💻 Author
Developed by Neet Jain

yaml
Copy
Edit




