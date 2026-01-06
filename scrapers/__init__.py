"""Web scrapers package."""

from .amazon_scraper import scrape_amazon
from .naukri_scraper import scrape_naukri

__all__ = ['scrape_amazon', 'scrape_naukri']
