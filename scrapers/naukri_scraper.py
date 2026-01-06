"""Naukri job scraper using Playwright sync API."""

import os
import sys
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright, Page

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.csv_utils import write_csv, generate_filename
from utils.dedupe import deduplicate_by_key
from utils.scraper_utils import wait_for_content


def extract_jobs_js(page: Page) -> List[Dict[str, Any]]:
    """Extract all job data from current page using JavaScript.

    Uses JS-side extraction for better performance.
    """
    script = """
    () => {
        const jobs = [];
        const cards = document.querySelectorAll('.srp-jobtuple-wrapper');

        cards.forEach(card => {
            const titleEl = card.querySelector('.title');
            const companyEl = card.querySelector('.comp-name');
            const expEl = card.querySelector('.expwdth');
            const salaryEl = card.querySelector('.sal-wrap span, .salary');
            const locationEl = card.querySelector('.locWdth');
            const linkEl = card.querySelector('a.title');
            const postedEl = card.querySelector('.job-post-day');

            jobs.push({
                title: titleEl ? titleEl.innerText.trim() : null,
                company: companyEl ? companyEl.innerText.trim() : null,
                experience: expEl ? expEl.innerText.trim() : null,
                salary: salaryEl ? salaryEl.innerText.trim() : null,
                location: locationEl ? locationEl.innerText.trim() : null,
                job_url: linkEl ? linkEl.href : null,
                posted: postedEl ? postedEl.innerText.trim() : null
            });
        });

        return jobs;
    }
    """
    try:
        return page.evaluate(script)
    except Exception as e:
        print(f"Error extracting jobs: {e}")
        return []


def scrape_naukri(keyword: str, location: str = '', max_pages: int = 5, output_dir: str = 'output') -> Optional[str]:
    """Scrape Naukri job listings for a given keyword.

    Args:
        keyword: Job search keyword
        location: Optional location filter
        max_pages: Maximum number of pages to scrape
        output_dir: Directory to save CSV output

    Returns:
        Path to the generated CSV file, or None if scraping failed
    """
    if not keyword or not keyword.strip():
        print("Error: Empty search keyword")
        return None

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    all_jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        try:
            # Navigate to Naukri
            page.goto("https://www.naukri.com/", wait_until='domcontentloaded')

            # Fill in keyword
            keyword_input = page.get_by_placeholder("Enter skills / designations / companies")
            keyword_input.fill(keyword.strip())

            # Fill in location if provided
            if location and location.strip():
                location_input = page.get_by_placeholder("Enter location")
                if location_input.count() > 0:
                    location_input.fill(location.strip())

            # Click search button
            page.locator(".qsbSubmit").click()

            # Wait for results to load
            if not wait_for_content(page, '.srp-jobtuple-wrapper', timeout=15000):
                print("No job listings found")
                browser.close()
                return None

            page_num = 1
            retry_count = 0
            max_retries = 3

            while page_num <= max_pages:
                print(f"Scraping page {page_num}...")

                # Wait for job cards to be visible
                if not wait_for_content(page, '.srp-jobtuple-wrapper', timeout=10000):
                    if retry_count < max_retries:
                        retry_count += 1
                        print(f"Retrying... ({retry_count}/{max_retries})")
                        continue
                    break

                # Extract jobs from current page
                jobs = extract_jobs_js(page)
                print(f"Found {len(jobs)} jobs on page {page_num}")

                if not jobs:
                    break

                all_jobs.extend(jobs)
                retry_count = 0  # Reset retry count on success

                # Try to go to next page
                next_button = page.get_by_role("link", name="Next")

                if next_button.count() == 0:
                    print("No next button found")
                    break

                if not next_button.first.is_visible():
                    print("Next button not visible")
                    break

                # Check if next button is disabled/hidden
                try:
                    next_button.first.click()
                    # Wait for new content to load
                    page.wait_for_load_state('networkidle', timeout=10000)
                    page_num += 1
                except Exception as e:
                    print(f"Failed to navigate to next page: {e}")
                    break

        except Exception as e:
            print(f"Scraping error: {e}")
        finally:
            browser.close()

    if not all_jobs:
        print("No jobs were scraped")
        return None

    # Deduplicate by job URL
    print(f"Total jobs before deduplication: {len(all_jobs)}")
    unique_jobs = deduplicate_by_key(all_jobs, 'job_url')
    print(f"Total jobs after deduplication: {len(unique_jobs)}")

    # Generate filename and save
    filename = generate_filename('naukri', keyword)
    filepath = os.path.join(output_dir, filename)

    fieldnames = ['title', 'company', 'experience', 'location', 'salary', 'job_url', 'posted']
    if write_csv(filepath, unique_jobs, fieldnames):
        print(f"Data saved to {filepath}")
        return filepath
    else:
        print("Failed to save CSV")
        return None


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Scrape Naukri job listings')
    parser.add_argument('keyword', help='Job search keyword')
    parser.add_argument('--location', default='', help='Location filter')
    parser.add_argument('--pages', type=int, default=5, help='Max pages to scrape')
    parser.add_argument('--output', default='output', help='Output directory')

    args = parser.parse_args()
    result = scrape_naukri(args.keyword, args.location, args.pages, args.output)

    if result:
        print(f"Successfully saved to: {result}")
    else:
        print("Scraping failed")
        sys.exit(1)
