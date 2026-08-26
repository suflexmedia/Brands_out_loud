"""Shared helpers used across public and admin routers."""

from common.auth import (
    COOKIE_NAME,
    is_authenticated,
    get_current_admin,
    require_admin,
    require_system_admin,
)
from common.text_utils import slugify, unique_slug
from common.cache_helpers import invalidate_blog_caches, invalidate_magazine_caches

__all__ = [
    "COOKIE_NAME",
    "is_authenticated",
    "get_current_admin",
    "require_admin",
    "require_system_admin",
    "slugify",
    "unique_slug",
    "invalidate_blog_caches",
    "invalidate_magazine_caches",
]
