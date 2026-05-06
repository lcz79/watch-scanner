"""Scrapers per le principali case d'aste mondiali."""
from .phillips_scraper import scrape_recent_results as phillips_recent, scrape_reference as phillips_reference
from .christies_scraper import scrape_recent_results as christies_recent, scrape_reference as christies_reference
from .sotherby_scraper import scrape_recent_results as sotherby_recent, scrape_reference as sotherby_reference
from .antiquorum_scraper import scrape_recent_results as antiquorum_recent, scrape_reference as antiquorum_reference

__all__ = [
    "phillips_recent", "phillips_reference",
    "christies_recent", "christies_reference",
    "sotherby_recent", "sotherby_reference",
    "antiquorum_recent", "antiquorum_reference",
]
