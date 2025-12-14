# AppSheet Provider Setup

This guide walks through configuring the Notes CLI/MCP server to use AppSheet as the backend.

## Prerequisites

- An AppSheet app with a notes table
- AppSheet API access enabled for your app
- Your AppSheet App ID and API Key

## Getting Your AppSheet Credentials

### 1. Find Your App ID

1. Open your AppSheet app in the editor
2. Go to **Settings** > **Integrations** > **IN: from cloud services to your app**
3. Enable the API if not already enabled
4. Copy the **App Id** (a GUID format identifier)

### 2. Get Your API Key

1. In the same Integrations section, find **Application Access Keys**
2. Click **Create Application Access Key**
3. Copy the generated key (you can only see it once)

## Table Structure

The AppSheet provider expects a `Note` table with these columns:

| Column | Type | Description |
|--------|------|-------------|
| `ID` | Key | Unique identifier (auto-generated) |
| `Title` | Text | Note title |
| `Content` | LongText | Note body |
| `Labels` | Text | Comma-separated labels |
| `Created` | DateTime | Creation timestamp |
| `Modified` | DateTime | Last modified timestamp |

Optional `Attachment` table for attachments:

| Column | Type | Description |
|--------|------|-------------|
| `ID` | Key | Unique identifier |
| `Note` | Ref | Reference to Note table |
| `Type` | Enum | "Image" or "Link" |
| `Image` | Image | Image file path |
| `Link` | Url | Link JSON with Url and LinkText |

## Configuration

### 1. Create a Config File

Create a JSON file (e.g., `notes-config.json`) with your credentials:

```json
{
  "provider": "appsheet",
  "appsheet": {
    "app_id": "YOUR_APP_ID",
    "api_key": "YOUR_API_KEY",
    "note_table": "Note",
    "attachment_table": "Attachment"
  }
}
```

Replace:
- `YOUR_APP_ID` with your AppSheet App Id
- `YOUR_API_KEY` with your Application Access Key

### 2. Import the Configuration

```bash
notes config import notes-config.json
```

This will:
1. Validate the configuration format
2. Test the connection to your AppSheet app
3. Save the config to `~/.config/notes/config.json`

If validation fails, your existing config remains unchanged.

### 3. Verify the Setup

```bash
notes config show
```

You should see output like:

```
Provider: appsheet
AppSheet Configuration:
  App ID: your-app-id-guid
  API Key: ********...abcd1234
  Note Table: Note
  Attachment Table: Attachment
  Connection: OK (1847 notes found)
```

### 4. Test with a Query

```bash
notes list --limit 3
```

## Security Notes

- **API Key Storage**: The API key is stored in `~/.config/notes/config.json` with restricted permissions
- **MCP Exposure**: The MCP server's `show_config` tool intentionally hides the API key - only the last 8 characters are shown
- **Config File**: Delete the temporary `notes-config.json` after importing

## Troubleshooting

### "AppSheet API error: 401"

Your API key is invalid or expired. Generate a new Application Access Key in AppSheet.

### "AppSheet API error: 404"

The table name doesn't match. Verify `note_table` and `attachment_table` match your actual table names (case-sensitive).

### "Connection failed"

- Ensure API is enabled in AppSheet (Settings > Integrations)
- Check that your App ID is correct
- Verify network connectivity

### Empty Results

- Check that your table name is correct (usually "Note" singular, not "Notes")
- Verify the table has data in AppSheet

## Next Steps

After configuring the AppSheet provider:

1. **Configure MCP**: Set up Claude Code or Gemini CLI integration
   - [Claude Code Setup](./CLAUDE-CODE.md)
   - [Gemini CLI Setup](./GEMINI-CLI.md)

2. **Use the CLI**: Start managing notes
   ```bash
   notes list
   notes add "My first note" -l "Test"
   ```
