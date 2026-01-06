"""Amazon product scraper using Playwright sync API."""

import os
import sys
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright, Page

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.csv_utils import write_csv, generate_filename
from utils.dedupe import deduplicate_by_key
from utils.scraper_utils import wait_for_content, has_next_page


def extract_products_js(page: Page) -> List[Dict[str, Any]]:
    """Extract all product data from current page using JavaScript.

    Uses JS-side extraction for better performance.
    """
    script = """
    () => {
        const products = [];
        const cards = document.querySelectorAll('[data-component-type="s-search-result"]');

        cards.forEach(card => {
            // Skip sponsored/ad cards if they don't have proper product data
            const titleEl = card.querySelector('h2 span');
            if (!titleEl) return;

            const priceWhole = card.querySelector('.a-price-whole');
            const ratingEl = card.querySelector('span.a-icon-alt');
            const reviewsEl = card.querySelector('span[aria-label*="stars"] + span span');
            const linkEl = card.querySelector('a.a-link-normal.s-no-outline, h2 a.a-link-normal');

            // Build product URL
            let productUrl = null;
            if (linkEl) {
                const href = linkEl.getAttribute('href');
                if (href) {
                    productUrl = href.startsWith('http') ? href : 'https://www.amazon.in' + href;
                    // Clean up URL - remove ref parameters for cleaner deduplication
                    const urlParts = productUrl.split('/ref=');
                    productUrl = urlParts[0];
                }
            }

            products.push({
                title: titleEl ? titleEl.innerText.trim() : null,
                price: priceWhole ? priceWhole.innerText.replace(/,/g, '').trim() : null,
                rating: ratingEl ? ratingEl.innerText.split(' ')[0] : null,
                reviews: reviewsEl ? reviewsEl.innerText.replace(/,/g, '').trim() : null,
                product_url: productUrl
            });
        });

        return products;
    }
    """
    try:
        return page.evaluate(script)
    except Exception as e:
        print(f"Error extracting products: {e}")
        return []


def scrape_amazon(query: str, max_pages: int = 5, output_dir: str = 'output') -> Optional[str]:
    """Scrape Amazon search results for a given query.

    Args:
        query: Search term
        max_pages: Maximum number of pages to scrape
        output_dir: Directory to save CSV output

    Returns:
        Path to the generated CSV file, or None if scraping failed
    """
    if not query or not query.strip():
        print("Error: Empty search query")
        return None

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    all_products = []
    encoded_query = quote_plus(query.strip())
    base_url = f"https://www.amazon.in/s?k={encoded_query}"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-IN',
            timezone_id='Asia/Kolkata',
        )
        page = context.new_page()

        try:
            page_num = 1

            while page_num <= max_pages:
                url = f"{base_url}&page={page_num}"
                print(f"Scraping page {page_num}: {url}")

                page.goto(url, wait_until='load', timeout=60000)

                # Wait for product grid to load
                if not wait_for_content(page, '[data-component-type="s-search-result"]', timeout=15000):
                    print(f"No products found on page {page_num}")
                    break

                # Extract products from current page
                products = extract_products_js(page)
                print(f"Found {len(products)} products on page {page_num}")

                if not products:
                    break

                all_products.extend(products)

                # Check for next page
                next_button = page.locator('a.s-pagination-next')
                if next_button.count() == 0 or not next_button.first.is_visible():
                    print("No more pages available")
                    break

                # Check if next button is disabled
                next_class = next_button.first.get_attribute('class') or ''
                if 'disabled' in next_class.lower():
                    print("Next button is disabled")
                    break

                page_num += 1

        except Exception as e:
            print(f"Scraping error: {e}")
        finally:
            browser.close()

    if not all_products:
        print("No products were scraped")
        return None

    # Deduplicate by product URL
    print(f"Total products before deduplication: {len(all_products)}")
    unique_products = deduplicate_by_key(all_products, 'product_url')
    print(f"Total products after deduplication: {len(unique_products)}")

    # Generate filename and save
    filename = generate_filename('amazon', query)
    filepath = os.path.join(output_dir, filename)

    fieldnames = ['title', 'price', 'rating', 'reviews', 'product_url']
    if write_csv(filepath, unique_products, fieldnames):
        print(f"Data saved to {filepath}")
        return filepath
    else:
        print("Failed to save CSV")
        return None


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Scrape Amazon products')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--pages', type=int, default=5, help='Max pages to scrape')
    parser.add_argument('--output', default='output', help='Output directory')

    args = parser.parse_args()
    result = scrape_amazon(args.query, args.pages, args.output)

    if result:
        print(f"Successfully saved to: {result}")
    else:
        print("Scraping failed")
        sys.exit(1)
