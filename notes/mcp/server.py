"""Notes MCP Server - Expose notes SDK via MCP protocol."""

from mcp.server.fastmcp import FastMCP

from notes.sdk.providers import get_provider
from notes.sdk.config import load_config

# Initialize MCP server
mcp = FastMCP("notes")


@mcp.tool()
def show_config() -> dict:
    """Show current notes configuration (sensitive values hidden).

    Returns:
        dict with provider type and non-sensitive settings.
        API keys and secrets are never exposed.
    """
    config = load_config()
    if not config:
        return {"error": "No config found. Run 'notes config import <file>' via CLI."}

    provider = config.get("provider", "unknown")
    result = {"provider": provider}

    # Expose only non-sensitive fields per provider
    if provider == "appsheet":
        appsheet = config.get("appsheet", {})
        result["appsheet"] = {
            "app_id": appsheet.get("app_id", "(not set)"),
            "note_table": appsheet.get("note_table", "(not set)"),
            "attachment_table": appsheet.get("attachment_table", "(not set)"),
            # api_key intentionally omitted
        }

    return result


@mcp.tool()
def list_notes(
    query: str = "",
    limit: int = 50,
    sort: str = "",
) -> dict:
    """List and search notes using Gmail-style query syntax.

    Args:
        query: Gmail-style search query. Supports:

            TEXT SEARCH (searches title and content):
              "meeting"           - notes containing "meeting"
              "project update"    - notes containing both words (implicit AND)
              "exact phrase"      - use quotes for exact phrase

            LABEL FILTERS:
              label:work          - notes with "work" label
              label:personal      - notes with "personal" label
              -label:archived     - exclude notes with "archived" label

            COMBINING FILTERS:
              meeting label:work           - "meeting" AND work label
              meeting -label:archived      - "meeting" but NOT archived
              label:work OR label:personal - either label
              (label:work OR label:home) meeting - grouping with parens

            EXAMPLES:
              "meeting"                     - search for "meeting" anywhere
              "label:work"                  - all notes labeled work
              "meeting -label:archived"    - meeting but not archived
              "label:work OR label:personal" - notes with either label

        limit: Maximum notes to return (default 50)

        sort: Sort field, prefix with - for descending.
              Examples: "modified", "-modified", "created", "-created"

    Returns:
        dict with:
          - results: list of note objects (ID, Title, Content, Labels, Modified, etc.)
          - total_count: total matching notes (may be > len(results) if limited)
    """
    provider = get_provider()
    return provider.list(
        query=query if query else None,
        limit=limit,
        sort=sort if sort else None,
    )


@mcp.tool()
def add_note(
    title: str,
    content: str = "",
    labels: str = "",
) -> dict:
    """Create a new note.

    Args:
        title: Note title (required)
        content: Note body/content (optional)
        labels: Comma-separated labels (optional).
                Examples: "Work", "Work,Todo", "Personal,Important"

    Returns:
        Created note object with ID, Title, Content, Labels, Created, Modified, etc.
    """
    provider = get_provider()
    return provider.add(title=title, content=content, labels=labels)


@mcp.tool()
def read_note(note_id: str) -> dict:
    """Read a single note by ID.

    Args:
        note_id: The note ID to retrieve (from list_notes results)

    Returns:
        Note object with ID, Title, Content, Labels, Created, Modified, etc.
        Returns {"error": "Note not found"} if the note doesn't exist.
    """
    provider = get_provider()
    note = provider.get(note_id=note_id)
    if note is None:
        return {"error": "Note not found", "note_id": note_id}
    return note


@mcp.tool()
def update_note(
    note_id: str,
    title: str | None = None,
    content: str | None = None,
    labels: str | None = None,
) -> dict:
    """Update an existing note.

    Only specified fields are updated; others remain unchanged.

    Args:
        note_id: The note ID to update (required)
        title: New title (optional)
        content: New content/body (optional)
        labels: New labels as comma-separated string (optional).
                Examples: "Work", "Work,Todo", "Personal,Important"

    Returns:
        Updated note object with ID, Title, Content, Labels, Modified, etc.
    """
    if title is None and content is None and labels is None:
        return {"error": "At least one of title, content, or labels must be provided"}

    provider = get_provider()
    return provider.update(note_id=note_id, title=title, content=content, labels=labels)


@mcp.tool()
def list_attachments(note_id: str) -> list[dict]:
    """List attachments for a note.

    Args:
        note_id: The note ID to get attachments for (from list_notes results)

    Returns:
        List of attachment objects with:
          - ID: attachment ID
          - Type: "Image" or "Link"
          - Image: file path like "Attachment_Images/filename.jpg" (for images)
          - Link: JSON string with Url and LinkText (for links)
    """
    provider = get_provider()
    return provider.list_attachments(note_id=note_id)


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
