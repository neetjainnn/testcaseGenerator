# 🧪 Automated Test Case Generator from Jira & Confluence

This Python automation script connects to **Jira and Confluence**, reads issue and document content, and automatically generates test cases using **Google Gemini (Generative AI)**. It attaches those test cases back to the Jira issues and sends updates to **Slack**.

---

## 🚀 Features

- Fetches Jira Sprint details using Board Name and Sprint ID
- Extracts:
  - Issue Summary
  - Issue Description
  - `.txt` attachments
  - Sprint Goal (Confluence URL)
- Generates 30–40 scenario-based test cases via Google Gemini API
- Saves test cases in Excel format
- Attaches Excel file back to respective Jira issue
- Sends notification to Slack
- Caches processed items to avoid duplication

---

## 🛠️ Setup Instructions

### 1. 🔧 Install Dependencies

```bash
pip install requests pandas beautifulsoup4 openpyxl
2. 🧾 Create config.json
Add all your Jira domain configurations in the following format:

json
Copy
Edit
{
  "your-domain.atlassian.net": {
    "JIRA_BASE": "https://your-domain.atlassian.net",
    "JIRA_EMAIL": "your-email@example.com",
    "JIRA_API_TOKEN": "your-jira-api-token",
    "CONFLUENCE_BASE": "https://your-domain.atlassian.net/wiki",
    "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/...",
    "GEMINI_API_KEY": "your-gemini-api-key"
  },
  "another-domain.atlassian.net": {
    "JIRA_BASE": "https://another-domain.atlassian.net",
    "JIRA_EMAIL": "another-email@example.com",
    "JIRA_API_TOKEN": "another-api-token",
    "CONFLUENCE_BASE": "https://another-domain.atlassian.net/wiki",
    "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/...",
    "GEMINI_API_KEY": "another-gemini-api-key"
  }
}
🔐 Keep this file secure. Do not upload it to GitHub.

3. 🖥️ Run the Script
bash
Copy
Edit
python auto_testcase_generator.py
You'll be prompted to enter:

Sprint Board Name (e.g., SYMBO Scrum)

Sprint ID (e.g., 328)

You can find these in your Jira backlog or URL.

📁 Files & Output
Generated test cases are saved as .xlsx files (Excel)

Each file is attached to Jira issues automatically

Already-processed Confluence pages and issues are tracked in:

pgsql
Copy
Edit
processed_confluence_pages.json
💡 Notes
✅ Test cases are generated only once per unique issue or page

🧠 Uses Google Gemini Flash model for fast & structured response

⚠️ Sprint name is not used — you must provide the correct Sprint ID

💬 Errors and updates are sent to your configured Slack channel

🤝 Contributions
Pull requests are welcome. For major changes, please open an issue first to discuss your ideas.

📜 License
This project is for internal use and automation. Feel free to customize it as needed.

