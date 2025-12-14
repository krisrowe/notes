# Configuring Notes MCP Server with Gemini CLI

This document outlines how to configure the Notes MCP Server for use with Gemini CLI and Gemini Code Assist extension in VS Code.

**Note:** Gemini CLI and Gemini Code Assist (VS Code) share the same configuration. IntelliJ's Gemini Code Assist plugin does not currently support MCP servers.

## Prerequisites

- **Notes Installed:** Install via pipx (see main [README.md](../README.md))
- **Provider Configured:** Complete setup for your chosen provider (e.g., [AppSheet](./APPSHEET.md))
- **Gemini CLI or Gemini Code Assist Installed:**
  - For Gemini CLI: [Install Gemini CLI](https://google-gemini.github.io/gemini-cli/)
  - For Gemini Code Assist: Install from the VS Code marketplace

## Quick Start

```bash
gemini mcp add notes --command notes-mcp --scope user
```

This adds the Notes MCP server to your user scope so it's available everywhere.

## Shared Configuration

**Important:** Gemini CLI and Gemini Code Assist extension in VS Code share the same configuration system. When you configure the MCP server using `gemini mcp add`, the configuration is automatically available to both clients.

Both read from:
- `~/.gemini/settings.json` (user scope)
- `.gemini/settings.json` (project scope)

## Configuration Options

### Using `gemini mcp add` Command

```bash
# Remove any existing configuration first (if updating)
gemini mcp remove notes --scope user

# Add the Notes MCP server
gemini mcp add notes --command notes-mcp --scope user
```

**Note:** Use `--scope user` to make the server available from any directory. If omitted, the server is configured for project scope only.

### Manual Configuration

**User scope** (`~/.gemini/settings.json`):

```json
{
  "mcpServers": {
    "notes": {
      "command": "notes-mcp",
      "args": []
    }
  }
}
```

**Project scope** (`.gemini/settings.json` in your project):

```json
{
  "mcpServers": {
    "notes": {
      "command": "notes-mcp",
      "args": []
    }
  }
}
```

## Configuration File Locations

| Scope | Location | When to Use |
|-------|----------|-------------|
| User | `~/.gemini/settings.json` | Personal use across all directories (recommended) |
| Project | `.gemini/settings.json` | Project-specific configuration |

For Notes, **user scope is recommended** since you'll want note access from various projects.

## Verifying Configuration

```bash
gemini mcp list
```

You should see output like:

```
Configured MCP servers:

✓ notes: notes-mcp (stdio) - Connected
```

## Using with Gemini CLI

Once configured, interact naturally:

**With Gemini CLI:**
- "What notes do I have labeled 'work'?"
- "Create a note titled 'Meeting Notes' about today's discussion"
- "Search my notes for anything about the project deadline"
- "List notes that aren't archived"

**With Gemini Code Assist (VS Code):**
- Use natural language in the chat interface
- The extension automatically uses the configured MCP server

## Managing Servers

```bash
# Remove the server
gemini mcp remove notes --scope user

# Update by removing and re-adding
gemini mcp remove notes --scope user
gemini mcp add notes --command notes-mcp --scope user
```

## Troubleshooting

**Server shows as "Disconnected":**
- Ensure notes is installed: `notes --version`
- Check provider config: `notes config show`
- Test the CLI directly: `notes list --limit 1`

**"No config found" errors:**
- Run `notes config import <your-config.json>` to configure a provider
- See [APPSHEET.md](./APPSHEET.md) for provider setup

### Debugging the Configuration

If you're having issues, check your `settings.json`:

```bash
cat ~/.gemini/settings.json
```

The `mcpServers` section should look like:

```json
{
  "mcpServers": {
    "notes": {
      "command": "notes-mcp",
      "args": []
    }
  }
}
```

**Common Mistakes:**
- Extra characters or incorrect quoting
- Wrong command name

If incorrect, remove and re-add the server.

## Security Considerations

**Config Storage:**
- Provider credentials are stored in `~/.config/notes/config.json`
- The MCP server's `show_config` tool never exposes full API keys

**File Permissions:**
```bash
chmod 600 ~/.config/notes/config.json
chmod 600 ~/.gemini/settings.json
```

## Notes for VS Code Users

- **Configuration Sharing:** Configuration created with `gemini mcp add` is automatically shared with Gemini Code Assist in VS Code
- **Restart Required:** After configuring, you may need to restart VS Code
- **Scope Behavior:**
  - User scope: Available in all VS Code workspaces
  - Project scope: Only available when opening that specific directory

---

For more details on Gemini CLI MCP server configuration, see the [official documentation](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html).
