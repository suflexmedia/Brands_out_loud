from .html_templates import *
from .rss import get_trending_news
import asyncio

def get_homepage():
    homepage = HOMEPAGE_BLANK_TEMPLATE.replace('[[[ARTICLES WILL BE ADDED HERE DYNAMICALLY]]]', asyncio.run(get_trending_news()))
    return homepage