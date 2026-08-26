"""Grouped cache invalidation so write endpoints cannot forget a key."""

from cache_manager import cache_manager


def invalidate_blog_caches() -> None:
    """Clears every cache entry that can contain blog-derived content."""
    cache_manager.invalidate("blogs")
    cache_manager.invalidate("navbar")
    cache_manager.invalidate("homepage")
    cache_manager.invalidate("blog_listing")
    cache_manager.invalidate("blog_categories")
    cache_manager.invalidate_pattern("related_blogs_")
    cache_manager.invalidate_pattern("blog_post_")
    cache_manager.invalidate_pattern("sitemap_")


def invalidate_magazine_caches() -> None:
    """Clears every cache entry that can contain magazine or book content."""
    cache_manager.invalidate("magazine_listing")
    cache_manager.invalidate("magazines")
    cache_manager.invalidate("magazines_grid")
    cache_manager.invalidate_pattern("magazine_issue_")
    cache_manager.invalidate_pattern("magazine_book_")
    cache_manager.invalidate_pattern("magazines_page_")
    cache_manager.invalidate_pattern("sitemap_")
