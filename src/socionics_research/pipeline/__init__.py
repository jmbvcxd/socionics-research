"""Data pipeline module for scraping, rewriting, and indexing."""

from .scraper import scrape_url, save_source

__all__ = ["scrape_url", "save_source"]
