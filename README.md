# Notes

A platform for managing notes with multiple backend providers.

## Installation

```bash
pip install -e .
```

## Configuration

Notes uses a central JSON config file stored at `~/.config/notes/config.json`.

### Setup with AppSheet Provider

1. Create a config file (e.g., `my-config.json`):

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

2. Import and validate the config:

```bash
notes config import my-config.json
```

This validates the config and tests the connection before saving. If validation fails, your existing config remains unchanged.

3. Verify the config:

```bash
notes config show
```

## Usage

### List and search notes

```bash
notes list                              # List all notes (default 50)
notes list --limit 10                   # Limit results
notes list --format json                # JSON output
notes list "meeting"                    # Search for "meeting"
notes list "label:work"                 # Filter by label
notes list "project -label:archived"    # Exclude label
notes list "label:work OR label:home"   # Either label
notes list --sort=-modified             # Sort by modified descending
```

### Query syntax

Gmail-style query syntax for searching and filtering:

| Query | Meaning |
|-------|---------|
| `meeting` | Text search in title and content |
| `"exact phrase"` | Phrase search |
| `label:work` | Filter by label |
| `-label:archived` | Exclude label |
| `meeting label:work` | Text AND label (implicit AND) |
| `label:work OR label:home` | Either label |
| `(label:a OR label:b) meeting` | Grouping with parentheses |

### Add notes

```bash
notes add "Meeting notes"
notes add "Shopping list" -c "Milk, eggs, bread"
notes add "Work task" -l "Work,Todo"
```

## MCP Server

Run the MCP server for integration with Claude Code or other MCP clients:

```bash
notes-mcp
```

Available tools:
- `list_notes(query, limit, sort)` - Search and list notes
- `add_note(title, content, labels)` - Create a note
- `show_config()` - Show config (API keys hidden)

## Providers

- **appsheet**: Connects to an AppSheet app via REST API
- **json**: (planned) Local JSON file storage
- **sheets**: (planned) Google Sheets backend via gwsa

## Future Enhancements

### Image Attachments via Google Drive

The AppSheet API supports referencing image files by path (e.g., `Attachment_Images/filename.jpg`). Testing confirmed that:

1. Creating an attachment record with an image path successfully displays the image in AppSheet UI
2. The `Image` column appears read-only via API, but `List Image` accepts paths
3. Images must exist in AppSheet's storage folder

**Proposed approach for full image support:**
1. Use gwsa to upload image files to the Google Drive folder backing AppSheet storage
2. Create attachment records via API referencing the uploaded filename
3. For retrieval, read the path from attachment records and fetch via Google Drive API

This would enable round-trip image attachment support without base64 encoding through the AppSheet API.

### File Existence Validation

When creating attachments via SDK/CLI/MCP with a filename reference, we should validate that the file exists in Google Drive before creating the attachment record. This prevents orphaned attachment records pointing to non-existent files.

### Other Planned Features

- Note read, update, and delete operations
- Additional providers (Google Sheets, local JSON, GCS bucket)
- Formal provider interface/abstract class with Pydantic data models
