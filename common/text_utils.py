"""Slug generation and normalisation helpers."""

import re
import unicodedata
from typing import Awaitable, Callable

_SLUG_STRIP = re.compile(r"[^a-z0-9\s-]")
_SLUG_SPACES = re.compile(r"[\s_-]+")
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def slugify(value: str) -> str:
    """Converts arbitrary text into a lowercase URL-safe hyphenated slug."""
    normalised = unicodedata.normalize("NFKD", value or "")
    ascii_only = normalised.encode("ascii", "ignore").decode("ascii")
    lowered = _SLUG_STRIP.sub("", ascii_only.lower())
    return _SLUG_SPACES.sub("-", lowered).strip("-")


async def unique_slug(base: str, exists: Callable[[str], Awaitable[bool]]) -> str:
    """Returns a slug derived from base that passes the caller's existence check."""
    root = slugify(base) or "item"
    candidate = root
    suffix = 2
    while await exists(candidate):
        candidate = f"{root}-{suffix}"
        suffix += 1
    return candidate
