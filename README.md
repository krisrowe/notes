# Notes

CLI and MCP Server for managing notes across multiple backends. Integrates with Claude Code, Gemini CLI, and other MCP-compatible clients.

## Quick Start

```bash
# Install
pipx install git+https://github.com/krisrowe/notes.git

# Configure your provider (see Provider Setup below)
notes config import my-config.json

# Configure MCP for Claude Code
claude mcp add --scope user notes -- notes-mcp

# Configure MCP for Gemini CLI
gemini mcp add notes --command notes-mcp --scope user
```

## Features

- **CLI Tool (`notes`)** - List, add, and search notes from the command line
- **MCP Server (`notes-mcp`)** - Note management for LLM clients
- **Gmail-style Query Syntax** - Search with `label:work`, `-label:archived`, `OR`, etc.
- **Multiple Providers** - AppSheet (now), Google Sheets and local JSON (planned)
- **Central Config** - Settings stored in `~/.config/notes/config.json`

## Prerequisites

- **Python 3.10+**
- **pipx** - For isolated installation ([install pipx](https://pipx.pypa.io/stable/installation/))
- **A configured provider** - See Provider Setup below

## Installation

### Install via pipx (Recommended)

```bash
pipx install git+https://github.com/krisrowe/notes.git
```

This installs both the `notes` CLI and `notes-mcp` server commands.

### Upgrade

```bash
pipx upgrade notes
```

### Uninstall

```bash
pipx uninstall notes
```

## Provider Setup

Notes requires a backend provider. Choose one and follow its setup guide:

| Provider | Status | Setup Guide |
|----------|--------|-------------|
| **AppSheet** | Available | [docs/APPSHEET.md](./docs/APPSHEET.md) |
| **Google Sheets** | Planned | - |
| **Local JSON** | Planned | - |

After configuring your provider, verify the setup:

```bash
notes config show
```

## MCP Client Configuration

### Claude Code

```bash
claude mcp add --scope user notes -- notes-mcp
```

For detailed options, see [docs/CLAUDE-CODE.md](./docs/CLAUDE-CODE.md).

### Gemini CLI

```bash
gemini mcp add notes --command notes-mcp --scope user
```

For detailed options, see [docs/GEMINI-CLI.md](./docs/GEMINI-CLI.md).

## CLI Usage

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

### List attachments

```bash
notes attachments list <note-id>
notes attachments list <note-id> --format json
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `notes list [query]` | List and search notes |
| `notes add <title>` | Create a new note |
| `notes attachments list <id>` | List attachments for a note |
| `notes config show` | Show current configuration |
| `notes config import <file>` | Import configuration from JSON |
| `notes --version` | Show version |
| `notes --help` | Show help |

## MCP Server Tools

The MCP server exposes these tools for LLM clients:

| Tool | Description |
|------|-------------|
| `list_notes` | Search and list notes with Gmail-style query |
| `add_note` | Create a new note with title, content, labels |
| `list_attachments` | List attachments for a note |
| `show_config` | Show config (API keys hidden) |

For detailed tool documentation, see [docs/TOOLS.md](./docs/TOOLS.md).

## Configuration Files

```
~/.config/notes/
└── config.json    # Provider settings (API keys stored here)
```

## Documentation

- [APPSHEET.md](./docs/APPSHEET.md) - AppSheet provider setup
- [CLAUDE-CODE.md](./docs/CLAUDE-CODE.md) - Claude Code MCP configuration
- [GEMINI-CLI.md](./docs/GEMINI-CLI.md) - Gemini CLI MCP configuration
- [TOOLS.md](./docs/TOOLS.md) - MCP tools reference

## Future Enhancements

- Note read, update, and delete operations
- Image attachment upload/download via Google Drive
- Additional providers (Google Sheets, local JSON)
- Formal provider interface with Pydantic data models

## License

MIT
