"""Notes CLI - Command-line interface for Notes."""

import json
import sys

from dotenv import load_dotenv
import click

from notes import __version__
from notes.sdk.providers import get_provider
from notes.sdk.config import (
    load_config,
    save_config,
    get_config_path,
    validate_and_show_config,
)


@click.group()
@click.version_option(version=__version__)
def notes():
    """Notes CLI - Manage notes across multiple backends."""
    pass


# Config command group
@click.group()
def config():
    """Manage configuration."""
    pass


@config.command("show")
def config_show():
    """Show current configuration and test connection."""
    existing = load_config()
    if not existing:
        click.echo(f"No config found at {get_config_path()}")
        click.echo("\nTo configure, create a JSON file and run:")
        click.echo("  notes config import <file.json>")
        click.echo("\nExample JSON for AppSheet:")
        example = {
            "provider": "appsheet",
            "appsheet": {
                "app_id": "your-app-id-guid",
                "api_key": "your-api-key",
                "note_table": "Note",
                "attachment_table": "Attachment"
            }
        }
        click.echo(json.dumps(example, indent=2))
        sys.exit(1)

    validate_and_show_config(existing)


@config.command("import")
@click.argument("file", type=click.Path(exists=True))
def config_import(file):
    """Import configuration from a JSON file.

    Validates the config and tests connection before saving.
    If validation fails, existing config is left unchanged.
    """
    # Load proposed config
    try:
        with open(file, "r") as f:
            proposed = json.load(f)
    except json.JSONDecodeError as e:
        click.secho(f"Invalid JSON: {e}", fg="red")
        sys.exit(1)
    except IOError as e:
        click.secho(f"Error reading file: {e}", fg="red")
        sys.exit(1)

    click.echo(f"Validating config from {file}...\n")

    # Validate and test connection
    if validate_and_show_config(proposed):
        # Success - save atomically
        save_config(proposed)
        click.echo(f"\nConfig saved to {get_config_path()}")
    else:
        click.secho("\nConfig import rejected - existing config unchanged.", fg="yellow")
        sys.exit(1)


@click.command()
@click.argument('query', required=False)
@click.option('--limit', default=50, help='Maximum notes to return (default 50).')
@click.option('--sort', help='Sort field. Prefix with - for descending (e.g., -modified).')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), default='text',
              help='Output format.')
def list_cmd(query, limit, sort, output_format):
    """List notes with optional Gmail-style query.

    \b
    Examples:
      notes list                          # List all notes
      notes list meeting                  # Search for "meeting"
      notes list "label:work"             # Filter by label
      notes list "meeting -label:archived"  # Exclude archived
      notes list --sort=-modified         # Sort by modified descending
    """
    try:
        provider = get_provider()
        result = provider.list(limit=limit, query=query, sort=sort)
        notes_list = result["results"]
        total = result["total_count"]

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2, default=str))
        else:
            showing = len(notes_list)
            if query:
                if showing < total:
                    click.echo(f"Showing {showing} of {total} matching notes:")
                else:
                    click.echo(f"Found {total} matching notes:")
            else:
                if showing < total:
                    click.echo(f"Showing {showing} of {total} notes:")
                else:
                    click.echo(f"Showing all {total} notes:")
            for note in notes_list:
                note_id = note.get('_RowNumber') or note.get('ID') or note.get('id', '?')
                title = note.get('Title') or note.get('title') or '(no title)'
                click.echo(f"  [{note_id}] {title}")

    except Exception as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@click.command()
@click.argument('title')
@click.option('--content', '-c', default='', help='Note content/body.')
@click.option('--label', '-l', default='', help='Labels (comma-separated).')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), default='text',
              help='Output format.')
def add_cmd(title, content, label, output_format):
    """Add a new note.

    \b
    Examples:
      notes add "Meeting notes"
      notes add "Shopping list" -c "Milk, eggs, bread"
      notes add "Work task" -l "Work,Todo"
    """
    try:
        provider = get_provider()
        note = provider.add(title=title, content=content, labels=label)

        if output_format == 'json':
            click.echo(json.dumps(note, indent=2, default=str))
        else:
            note_id = note.get('ID') or note.get('id', '?')
            click.secho(f"Created note [{note_id}]: {title}", fg='green')

    except Exception as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@click.command()
@click.argument('note_id')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), default='text',
              help='Output format.')
def read_cmd(note_id, output_format):
    """Read a note by ID.

    \b
    Examples:
      notes read f15775cf
      notes read f15775cf --format json
    """
    try:
        provider = get_provider()
        note = provider.get(note_id=note_id)

        if note is None:
            click.secho(f"Note not found: {note_id}", fg='yellow', err=True)
            sys.exit(1)

        if output_format == 'json':
            click.echo(json.dumps(note, indent=2, default=str))
        else:
            title = note.get('Title') or note.get('title') or '(no title)'
            content = note.get('Content') or note.get('content') or ''
            labels = note.get('Labels') or note.get('labels') or ''
            click.echo(f"[{note_id}] {title}")
            if labels:
                click.echo(f"Labels: {labels}")
            if content:
                click.echo(f"\n{content}")

    except Exception as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


@click.command()
@click.argument('note_id')
@click.option('--title', '-t', default=None, help='New title.')
@click.option('--content', '-c', default=None, help='New content/body.')
@click.option('--label', '-l', default=None, help='New labels (comma-separated).')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), default='text',
              help='Output format.')
def update_cmd(note_id, title, content, label, output_format):
    """Update an existing note.

    \b
    Examples:
      notes update f15775cf -t "New title"
      notes update f15775cf -c "Updated content"
      notes update f15775cf -l "Work,Important"
      notes update f15775cf -t "New title" -c "New content"
    """
    if title is None and content is None and label is None:
        click.secho("Error: At least one of --title, --content, or --label required.", fg='red', err=True)
        sys.exit(1)

    try:
        provider = get_provider()
        note = provider.update(note_id=note_id, title=title, content=content, labels=label)

        if output_format == 'json':
            click.echo(json.dumps(note, indent=2, default=str))
        else:
            updated_title = note.get('Title') or note.get('title') or '(no title)'
            click.secho(f"Updated note [{note_id}]: {updated_title}", fg='green')

    except Exception as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


# Attachments command group
@click.group()
def attachments():
    """Manage note attachments."""
    pass


@attachments.command("list")
@click.argument('note_id')
@click.option('--format', 'output_format', type=click.Choice(['json', 'text']), default='text',
              help='Output format.')
def attachments_list(note_id, output_format):
    """List attachments for a note.

    \b
    Examples:
      notes attachments list f15775cf
      notes attachments list f15775cf --format json
    """
    try:
        provider = get_provider()
        attachment_list = provider.list_attachments(note_id=note_id)

        if output_format == 'json':
            click.echo(json.dumps(attachment_list, indent=2, default=str))
        else:
            if not attachment_list:
                click.echo("No attachments found.")
            else:
                click.echo(f"Found {len(attachment_list)} attachments:")
                for att in attachment_list:
                    att_type = att.get('Type', '?')
                    if att_type == 'Image':
                        path = att.get('Image') or att.get('List Image', '(no path)')
                        click.echo(f"  [{att.get('ID', '?')}] Image: {path}")
                    elif att_type == 'Link':
                        link_json = att.get('Link', '{}')
                        click.echo(f"  [{att.get('ID', '?')}] Link: {link_json}")
                    else:
                        click.echo(f"  [{att.get('ID', '?')}] {att_type}")

    except Exception as e:
        click.secho(f"Error: {e}", fg='red', err=True)
        sys.exit(1)


notes.add_command(config)
notes.add_command(list_cmd, name='list')
notes.add_command(read_cmd, name='read')
notes.add_command(add_cmd, name='add')
notes.add_command(update_cmd, name='update')
notes.add_command(attachments)


def main():
    """Entry point for the CLI."""
    load_dotenv()
    notes()


if __name__ == "__main__":
    main()
