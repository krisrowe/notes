# MCP Tools Reference

This document provides detailed documentation for all tools exposed by the Notes MCP server.

## Tools Overview

| Tool | Description |
|------|-------------|
| `list_notes` | Search and list notes with Gmail-style query |
| `add_note` | Create a new note |
| `list_attachments` | List attachments for a note |
| `show_config` | Show current configuration |

---

## list_notes

Search and list notes using Gmail-style query syntax.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | No | `""` | Gmail-style search query |
| `limit` | integer | No | `50` | Maximum notes to return |
| `sort` | string | No | `""` | Sort field, prefix with `-` for descending |

### Query Syntax

The query parameter supports Gmail-style search syntax:

**Text Search** (searches title and content):
- `meeting` - notes containing "meeting"
- `project update` - notes containing both words (implicit AND)
- `"exact phrase"` - use quotes for exact phrase matching

**Label Filters:**
- `label:work` - notes with "work" label
- `label:personal` - notes with "personal" label
- `-label:archived` - exclude notes with "archived" label

**Combining Filters:**
- `meeting label:work` - "meeting" AND work label
- `meeting -label:archived` - "meeting" but NOT archived
- `label:work OR label:personal` - either label
- `(label:work OR label:home) meeting` - grouping with parentheses

### Sort Options

- `modified` - sort by modified date ascending
- `-modified` - sort by modified date descending
- `created` - sort by created date ascending
- `-created` - sort by created date descending

### Returns

```json
{
  "results": [
    {
      "ID": "abc123",
      "Title": "Meeting Notes",
      "Content": "Discussed project timeline...",
      "Labels": "Work,Meetings",
      "Created": "2024-01-15 10:30:00",
      "Modified": "2024-01-15 14:22:00"
    }
  ],
  "total_count": 42
}
```

### Examples

```
# List all notes (default 50)
list_notes()

# Search for "meeting"
list_notes(query="meeting")

# Filter by label
list_notes(query="label:work")

# Complex query
list_notes(query="meeting -label:archived", limit=10, sort="-modified")
```

---

## add_note

Create a new note.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `title` | string | **Yes** | - | Note title |
| `content` | string | No | `""` | Note body/content |
| `labels` | string | No | `""` | Comma-separated labels |

### Returns

```json
{
  "ID": "new-note-id",
  "Title": "My New Note",
  "Content": "Note content here",
  "Labels": "Work,Todo",
  "Created": "2024-01-15 16:00:00",
  "Modified": "2024-01-15 16:00:00"
}
```

### Examples

```
# Simple note
add_note(title="Quick reminder")

# Note with content
add_note(title="Meeting Notes", content="Discussed Q1 goals...")

# Note with labels
add_note(title="Project Task", content="Review PR #123", labels="Work,Todo")
```

---

## list_attachments

List attachments for a specific note.

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `note_id` | string | **Yes** | - | The note ID to get attachments for |

### Returns

```json
[
  {
    "ID": "att123",
    "Type": "Image",
    "Image": "Attachment_Images/photo.jpg",
    "Link": null
  },
  {
    "ID": "att456",
    "Type": "Link",
    "Image": null,
    "Link": "{\"Url\":\"https://example.com\",\"LinkText\":\"Example\"}"
  }
]
```

### Attachment Types

| Type | Description | Fields |
|------|-------------|--------|
| `Image` | Image file | `Image` contains file path |
| `Link` | URL link | `Link` contains JSON with `Url` and `LinkText` |

### Examples

```
# Get attachments for a note
list_attachments(note_id="abc123")
```

---

## show_config

Show current configuration (sensitive values hidden).

### Parameters

None.

### Returns

```json
{
  "provider": "appsheet",
  "appsheet": {
    "app_id": "your-app-id-guid",
    "note_table": "Note",
    "attachment_table": "Attachment"
  }
}
```

**Note:** API keys are intentionally never exposed through this tool.

### Error Response

If no configuration is found:

```json
{
  "error": "No config found. Run 'notes config import <file>' via CLI."
}
```

---

## Error Handling

All tools may return errors in the following format:

```json
{
  "error": "Error message describing what went wrong"
}
```

Common errors:
- `No config found` - Provider not configured
- `AppSheet API error: 401` - Invalid API key
- `AppSheet API error: 404` - Table not found
- `Connection failed` - Network or configuration issue
