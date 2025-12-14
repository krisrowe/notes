# Configuring Notes MCP Server with Claude Code

This document outlines how to configure the Notes MCP Server for use with Claude Code (the CLI tool).

## Prerequisites

- **Notes Installed:** Install via pipx (see main [README.md](../README.md))
- **Provider Configured:** Complete setup for your chosen provider (e.g., [AppSheet](./APPSHEET.md))
- **Claude Code Installed:** [Install Claude Code](https://docs.anthropic.com/en/docs/claude-code)

## Quick Start

```bash
claude mcp add --scope user notes -- notes-mcp
```

This adds the Notes MCP server to your user scope so it's available in all projects.

## Configuration Options

### Option A: Native Install (Recommended)

After installing notes via pipx:

```bash
claude mcp add --scope user notes -- notes-mcp
```

**Key points:**
- `--scope user` makes the server available across all projects
- `--` separates Claude's flags from the server command
- Uses config from `~/.config/notes/config.json` automatically

### Option B: Manual Configuration

For team sharing or more control, edit your Claude config file directly.

**User scope** (`~/.claude.json`):

```json
{
  "mcpServers": {
    "notes": {
      "type": "stdio",
      "command": "notes-mcp",
      "args": []
    }
  }
}
```

## Configuration Scope

| Scope | Location | Use Case |
|-------|----------|----------|
| `user` | `~/.claude.json` | Personal use across all projects (recommended) |
| `project` | `.mcp.json` in project root | Team sharing |
| `local` | Local to current session | Temporary testing |

For Notes, **user scope is recommended** since you'll want note access from various projects.

## Verifying Configuration

```bash
# List all configured MCP servers
claude mcp list

# Get details for the notes server
claude mcp get notes
```

Within a Claude Code session, use the `/mcp` command to check server status.

## Using with Claude Code

Once configured, interact naturally:

- "What notes do I have labeled 'work'?"
- "Create a note titled 'Meeting Notes' with today's action items"
- "Search my notes for 'project deadline'"
- "Show me notes that aren't archived"

## Managing Servers

```bash
# Remove the server
claude mcp remove notes --scope user

# Update by removing and re-adding
claude mcp remove notes --scope user
claude mcp add --scope user notes -- notes-mcp
```

## Troubleshooting

**Server not connecting:**
- Ensure notes is installed: `notes --version`
- Check provider config: `notes config show`
- Test the CLI directly: `notes list --limit 1`

**"No config found" errors:**
- Run `notes config import <your-config.json>` to configure a provider
- See [APPSHEET.md](./APPSHEET.md) for provider setup

**Permission errors:**
- Claude Code prompts for approval on project-scoped servers from `.mcp.json`
- User-scoped servers in `~/.claude.json` don't require approval

**Debug mode:**
For detailed server logs, run the server manually:
```bash
LOG_LEVEL=DEBUG notes-mcp
```

## Security Considerations

**Config Storage:**
- Provider credentials are stored in `~/.config/notes/config.json`
- The MCP server's `show_config` tool never exposes full API keys
- File permissions should be 600 (owner read/write only)

**File Permissions:**
```bash
chmod 600 ~/.config/notes/config.json
```

## Comparison with Other Clients

| Feature | Claude Code | Claude Desktop | Gemini CLI |
|---------|-------------|----------------|------------|
| Config file | `~/.claude.json` or `.mcp.json` | Platform-specific | `~/.gemini/settings.json` |
| Add command | `claude mcp add` | Manual JSON edit | `gemini mcp add` |
| Transport | stdio | stdio or HTTP | stdio or HTTP |
| Scope levels | user, project, local | N/A | user, project |

---

For more details on Claude Code MCP server configuration, see the [official documentation](https://docs.anthropic.com/en/docs/claude-code/mcp).
