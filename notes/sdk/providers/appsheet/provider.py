"""AppSheet API provider implementation."""

import os
from typing import Optional

import httpx

from ...query import (
    QueryExpr,
    TextSearch,
    LabelFilter,
    NotExpr,
    AndExpr,
    OrExpr,
    parse_query,
)


class AppSheetProvider:
    """Provider that connects to the AppSheet API."""

    # AppSheet API base URL
    BASE_URL = "https://api.appsheet.com/api/v2/apps"

    def __init__(
        self,
        app_id: Optional[str] = None,
        api_key: Optional[str] = None,
        table_name: Optional[str] = None,
    ):
        self.app_id = app_id or os.environ.get("APPSHEET_APP_ID")
        self.api_key = api_key or os.environ.get("APPSHEET_API_KEY")
        self.table_name = table_name or os.environ.get("APPSHEET_TABLE_NAME", "Note")

        if not self.app_id:
            raise ValueError("AppSheet app_id is required. Set APPSHEET_APP_ID env var or configure via 'notes config import'.")
        if not self.api_key:
            raise ValueError("AppSheet api_key is required. Set APPSHEET_API_KEY env var or configure via 'notes config import'.")

    def _get_headers(self) -> dict:
        """Get headers for API requests."""
        return {
            "ApplicationAccessKey": self.api_key,
            "Content-Type": "application/json",
        }

    def _get_url(self, table: Optional[str] = None) -> str:
        """Get the API URL for a table action."""
        table = table or self.table_name
        return f"{self.BASE_URL}/{self.app_id}/tables/{table}/Action"

    def _query_to_selector(self, expr: QueryExpr) -> str:
        """Convert query AST to AppSheet Selector expression."""
        if isinstance(expr, TextSearch):
            # Search across Title and Content
            escaped = expr.value.replace('"', '\\"')
            return f'CONTAINS(CONCATENATE([Title], " ", [Content]), "{escaped}")'

        elif isinstance(expr, LabelFilter):
            escaped = expr.value.replace('"', '\\"')
            return f'CONTAINS([Labels], "{escaped}")'

        elif isinstance(expr, NotExpr):
            inner = self._query_to_selector(expr.expr)
            return f"NOT({inner})"

        elif isinstance(expr, AndExpr):
            left = self._query_to_selector(expr.left)
            right = self._query_to_selector(expr.right)
            return f"AND({left}, {right})"

        elif isinstance(expr, OrExpr):
            left = self._query_to_selector(expr.left)
            right = self._query_to_selector(expr.right)
            return f"OR({left}, {right})"

        else:
            raise ValueError(f"Unknown expression type: {type(expr)}")

    def list(
        self,
        limit: int = 50,
        query: Optional[str] = None,
        sort: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """List notes. Standard provider interface.

        Args:
            limit: Max notes to return (default 50)
            query: Gmail-style query string. Examples:
                   - "meeting"                  Search in title/content
                   - "label:work"               Filter by label
                   - "meeting -label:archived"  Exclude a label
                   - "label:work OR label:home" Either label
            sort: Sort field. Prefix with - for descending. e.g. "-modified"

        Returns:
            dict with "results" (list of notes) and "total_count" (int)
        """
        # Build selector from query
        selector = None
        if query:
            ast = parse_query(query)
            if ast:
                condition = self._query_to_selector(ast)
                selector = f"Filter({self.table_name}, {condition})"

                # Wrap with OrderBy if sort specified
                if sort:
                    desc = sort.startswith("-")
                    field = sort.lstrip("-").capitalize()
                    selector = f"OrderBy({selector}, [{field}], {'TRUE' if desc else 'FALSE'})"
        elif sort:
            # Sort without filter
            desc = sort.startswith("-")
            field = sort.lstrip("-").capitalize()
            selector = f"OrderBy({self.table_name}, [{field}], {'TRUE' if desc else 'FALSE'})"

        # AppSheet Find action
        payload = {
            "Action": "Find",
            "Properties": {
                "Locale": "en-US",
            },
            "Rows": [],
        }

        if selector:
            payload["Properties"]["Selector"] = selector

        response = httpx.post(
            self._get_url(),
            headers=self._get_headers(),
            json=payload,
            timeout=30.0,
        )

        if response.status_code != 200:
            raise Exception(f"AppSheet API error: {response.status_code} - {response.text}")

        rows = response.json() if response.text else []
        total_count = len(rows)

        return {
            "results": rows[:limit],
            "total_count": total_count,
        }

    def add(self, title: str, content: str = "", labels: str = "", **kwargs) -> dict:
        """Add a note. Standard provider interface.

        Args:
            title: Note title (required)
            content: Note content/body
            labels: Comma-separated labels
            **kwargs: Additional fields

        Returns:
            Created note dict with ID
        """
        row = {
            "Title": title,
            "Content": content,
            "Labels": labels,
            **kwargs,
        }

        payload = {
            "Action": "Add",
            "Properties": {
                "Locale": "en-US",
            },
            "Rows": [row],
        }

        response = httpx.post(
            self._get_url(),
            headers=self._get_headers(),
            json=payload,
            timeout=30.0,
        )

        if response.status_code != 200:
            raise Exception(f"AppSheet API error: {response.status_code} - {response.text}")

        result = response.json()
        if result.get("Rows"):
            return result["Rows"][0]
        return result

    @classmethod
    def validate_config(cls, config: dict) -> tuple[bool, str, dict]:
        """Validate AppSheet provider config and test connection.

        Args:
            config: Full config dict with 'appsheet' key containing provider settings

        Returns:
            (success, message, stats) where stats contains connection details
        """
        appsheet = config.get("appsheet", {})

        # Check required fields
        required = ["app_id", "api_key", "note_table"]
        missing = [k for k in required if not appsheet.get(k)]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}", {}

        app_id = appsheet.get("app_id")
        api_key = appsheet.get("api_key")
        note_table = appsheet.get("note_table")
        attachment_table = appsheet.get("attachment_table")

        base_url = cls.BASE_URL
        headers = {
            "ApplicationAccessKey": api_key,
            "Content-Type": "application/json",
        }

        stats = {
            "app_id": app_id,
            "api_key_preview": f"{'*' * 8}...{api_key[-8:]}" if api_key else "(not set)",
            "note_table": note_table,
            "attachment_table": attachment_table or "(not configured)",
        }

        # Test Note table connection
        try:
            url = f"{base_url}/{app_id}/tables/{note_table}/Action"
            payload = {"Action": "Find", "Properties": {"Locale": "en-US"}}
            response = httpx.post(url, headers=headers, json=payload, timeout=30.0)

            if response.status_code != 200:
                return False, f"Note table error: HTTP {response.status_code}", stats

            notes = response.json() if response.text else []
            stats["note_count"] = len(notes)
        except Exception as e:
            return False, f"Connection failed: {e}", stats

        # Test Attachment table if configured
        if attachment_table:
            try:
                url = f"{base_url}/{app_id}/tables/{attachment_table}/Action"
                response = httpx.post(url, headers=headers, json=payload, timeout=30.0)

                if response.status_code == 200:
                    attachments = response.json() if response.text else []
                    stats["attachment_count"] = len(attachments)
                else:
                    stats["attachment_error"] = f"HTTP {response.status_code}"
            except Exception as e:
                stats["attachment_error"] = str(e)

        return True, "Connection successful", stats
