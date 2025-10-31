# MCP Redmine

MCP Redmine connects Claude Desktop (or other MCP clients) to a Redmine instance, providing tools to interact with the Redmine API. This project is based on the original work by [Rune Kaagaard](https://github.com/runekaagaard/mcp-redmine).

## Installation

1. Clone the repository and install dependencies:

   ```bash
   git clone https://github.com/runekaagaard/mcp-redmine.git
   cd mcp-redmine
   pip install -r requirements.txt
   ```

2. Run the server:

   ```bash
   python server.py
   ```

## Basic Configuration

Set the following environment variables:

- `REDMINE_URL`: Base URL of your Redmine instance (required).

Each user must configure their API key (`redmine_api_key`) in the chat context (e.g., LibreChat). This allows personalized access to the Redmine API.

## Example Usage

Create a new issue in Redmine:

```bash
curl -X POST \
  -H "X-Redmine-API-Key: <your_api_key>" \
  -H "Content-Type: application/json" \
  -d '{
    "issue": {
      "project_id": 1,
      "subject": "New Issue",
      "description": "Issue description",
      "priority_id": 4
    }
  }' \
  <REDMINE_URL>/issues.json
```

## License

Mozilla Public License Version 2.0
