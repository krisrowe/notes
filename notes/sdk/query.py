"""Gmail-style query parser for notes.

Supports:
  - word           Text search across title/content
  - "phrase"       Exact phrase search
  - label:value    Filter by label
  - -term          NOT (exclude)
  - term1 term2    Implicit AND
  - term1 OR term2 Explicit OR
  - (group)        Grouping

Examples:
  meeting                        -> search for "meeting" in any field
  meeting -label:archived        -> meeting but not archived label
  label:work OR label:personal   -> either label
  "exact phrase" label:work      -> phrase AND label
"""

import re
from dataclasses import dataclass
from typing import Union


@dataclass
class TextSearch:
    """Search for text in title/content."""
    value: str


@dataclass
class LabelFilter:
    """Filter by label."""
    value: str


@dataclass
class NotExpr:
    """Negation."""
    expr: "QueryExpr"


@dataclass
class AndExpr:
    """Logical AND."""
    left: "QueryExpr"
    right: "QueryExpr"


@dataclass
class OrExpr:
    """Logical OR."""
    left: "QueryExpr"
    right: "QueryExpr"


# Union of all expression types
QueryExpr = Union[TextSearch, LabelFilter, NotExpr, AndExpr, OrExpr]


class QueryParser:
    """Parse Gmail-style query strings into an AST."""

    def __init__(self, query: str):
        self.query = query
        self.pos = 0
        self.tokens = self._tokenize(query)
        self.token_pos = 0

    def _tokenize(self, query: str) -> list[str]:
        """Tokenize query string."""
        tokens = []
        i = 0
        while i < len(query):
            # Skip whitespace
            if query[i].isspace():
                i += 1
                continue

            # Quoted string
            if query[i] == '"':
                j = i + 1
                while j < len(query) and query[j] != '"':
                    j += 1
                tokens.append(query[i:j + 1] if j < len(query) else query[i:j])
                i = j + 1
                continue

            # Parentheses
            if query[i] in '()':
                tokens.append(query[i])
                i += 1
                continue

            # Word (including label:value, -prefix)
            j = i
            while j < len(query) and not query[j].isspace() and query[j] not in '()':
                if query[j] == '"':
                    break
                j += 1
            if j > i:
                tokens.append(query[i:j])
            i = j

        return tokens

    def parse(self) -> QueryExpr | None:
        """Parse the query and return AST."""
        if not self.tokens:
            return None
        return self._parse_or()

    def _current(self) -> str | None:
        """Get current token."""
        if self.token_pos < len(self.tokens):
            return self.tokens[self.token_pos]
        return None

    def _advance(self) -> str | None:
        """Advance and return current token."""
        token = self._current()
        self.token_pos += 1
        return token

    def _parse_or(self) -> QueryExpr | None:
        """Parse OR expressions (lowest precedence)."""
        left = self._parse_and()
        if left is None:
            return None

        while self._current() and self._current().upper() == "OR":
            self._advance()  # consume OR
            right = self._parse_and()
            if right is None:
                break
            left = OrExpr(left, right)

        return left

    def _parse_and(self) -> QueryExpr | None:
        """Parse AND expressions (implicit between terms)."""
        left = self._parse_unary()
        if left is None:
            return None

        # Implicit AND: consecutive terms without OR
        while self._current() and self._current().upper() != "OR" and self._current() != ")":
            right = self._parse_unary()
            if right is None:
                break
            left = AndExpr(left, right)

        return left

    def _parse_unary(self) -> QueryExpr | None:
        """Parse unary expressions (NOT with - prefix)."""
        token = self._current()
        if token is None:
            return None

        # Handle negation prefix
        if token.startswith("-") and len(token) > 1:
            self._advance()
            # Parse the rest as an atom
            inner = self._parse_atom_from_token(token[1:])
            if inner:
                return NotExpr(inner)
            return None

        return self._parse_atom()

    def _parse_atom(self) -> QueryExpr | None:
        """Parse atomic expressions."""
        token = self._current()
        if token is None:
            return None

        # Parenthesized group
        if token == "(":
            self._advance()  # consume (
            expr = self._parse_or()
            if self._current() == ")":
                self._advance()  # consume )
            return expr

        self._advance()
        return self._parse_atom_from_token(token)

    def _parse_atom_from_token(self, token: str) -> QueryExpr | None:
        """Parse a single token into an expression."""
        # Quoted string -> text search
        if token.startswith('"'):
            value = token.strip('"')
            return TextSearch(value)

        # label:value -> label filter
        if token.lower().startswith("label:"):
            value = token[6:]
            return LabelFilter(value)

        # Plain word -> text search
        return TextSearch(token)


def parse_query(query: str) -> QueryExpr | None:
    """Parse a Gmail-style query string.

    Args:
        query: Query string like 'meeting -label:archived'

    Returns:
        QueryExpr AST or None if empty
    """
    if not query or not query.strip():
        return None
    return QueryParser(query.strip()).parse()
