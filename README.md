
# Test Case Automation Generator

Automates test case generation and attachment for Jira issues using Confluence documents, issue descriptions, summaries, and text attachments. Test cases are generated via Google Gemini API and attached to issues, with Slack notifications for each action.

## Features
- Multi-domain support via `config.json`
- Processes all active sprints and issues
- For each sprint:
  - If a Confluence document is in the sprint goal, generates test cases and attaches the same file to all issues
- For each issue:
  - Combines summary, description, and all `.txt` attachments into one master document
  - Generates a single master test case file and attaches it to the issue
  - Sends a Slack notification for each attachment
- Deduplication: No duplicate test case generation for the same content

## Setup
1. Clone the repository
2. Create and fill out `config.json` with your Jira/Confluence/Slack credentials
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set your Gemini API key in the script or config

## Usage
Run the main script:
```bash
python auto_testcase_generator.py
```

## Configuration
- `config.json` should contain domain-specific credentials and URLs for Jira, Confluence, and Slack.
- Example:
```json
{
  "your-domain.atlassian.net": {
    "JIRA_BASE": "https://your-domain.atlassian.net",
    "JIRA_EMAIL": "your-email",
    "JIRA_API_TOKEN": "your-token",
    "CONFLUENCE_BASE": "https://your-domain.atlassian.net/wiki",
    "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/..."
  }
}
```

## Output
- Excel files with generated test cases are attached to Jira issues automatically.
- Slack notifications are sent for each test case attachment.

## Key Files
- `auto_testcase_generator.py`: Main automation script
- `config.json`: Domain and credential configuration
- `processed_confluence_pages.json`: Tracks processed content to prevent duplicates

## Requirements
See `requirements.txt` for dependencies.

## Security
- **Never commit your `config.json`!** It is excluded by `.gitignore`.
- Keep your API tokens and credentials secure.

## License
MIT

## License
MIT
