# Test Case Automation

This project automates the generation of scenario-based test cases from Confluence documents and attaches them to Jira issues for all active sprints across multiple Jira/Confluence domains.

## Features
- Supports multiple organizations/domains via a single `config.json` file
- Generates 30–40 scenario-based test cases from Confluence page text using Gemini API
- Attaches the generated Excel file to all issues in each sprint
- Sends Slack notifications for status and errors
- Robust logging for debugging

## Setup
1. **Clone the repository**
2. **Create and fill in `config.json`** (see example below)
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the automation:**
   ```bash
   python auto_runner.py
   ```

## Example `config.json`
```json
{
  "yourdomain.atlassian.net": {
    "JIRA_BASE": "https://yourdomain.atlassian.net",
    "CONFLUENCE_BASE": "https://yourdomain.atlassian.net/wiki",
    "JIRA_EMAIL": "your_email@yourdomain.com",
    "JIRA_API_TOKEN": "your_api_token",
    "SLACK_WEBHOOK_URL": "your_slack_webhook"
  }
}
```

## Security
- **Never commit your `config.json`!** It is excluded by `.gitignore`.
- Keep your API tokens and credentials secure.

## License
MIT
