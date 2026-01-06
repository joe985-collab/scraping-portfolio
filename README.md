A very Basic Scraping project. Only for testing and demonstration purposes.

---

## Web Scraper Suite

This project includes two Playwright-based web scrapers with a Flask web UI:

1. **Amazon Product Scraper** - Search and scrape product listings from Amazon India
2. **Naukri Job Scraper** - Search and scrape job listings from Naukri.com

### Features

- Playwright sync API for reliable browser automation
- Flask web interface for easy searching
- CSV export with automatic deduplication
- Pagination support
- Background scraping (UI doesn't block)

---

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

---

## Usage

### Web Interface (Recommended)

Start the Flask application:

```bash
python app.py
```

Then open http://localhost:5000 in your browser.

- **Home** (`/`) - Choose between Amazon or Naukri scraper
- **Amazon** (`/amazon`) - Enter product keywords to search
- **Naukri** (`/naukri`) - Enter job keywords and optional location

Results are displayed in a table and can be downloaded as CSV.

### Command Line

#### Amazon Scraper

```bash
python -m scrapers.amazon_scraper "laptop stand" --pages 3 --output output
```

Options:
- `query` - Search term (required)
- `--pages` - Maximum pages to scrape (default: 5)
- `--output` - Output directory (default: output)

#### Naukri Scraper

```bash
python -m scrapers.naukri_scraper "data engineer" --location bangalore --pages 3 --output output
```

Options:
- `keyword` - Job search keyword (required)
- `--location` - Location filter (optional)
- `--pages` - Maximum pages to scrape (default: 5)
- `--output` - Output directory (default: output)

---

## Project Structure

```
e_commerce_scraper/
├── app.py                 # Flask web application
├── requirements.txt       # Python dependencies
├── DESIGN.MD              # Design document
├── scrapers/
│   ├── amazon_scraper.py  # Amazon product scraper
│   └── naukri_scraper.py  # Naukri job scraper
├── utils/
│   ├── csv_utils.py       # CSV read/write utilities
│   ├── dedupe.py          # Deduplication utilities
│   └── scraper_utils.py   # Shared scraper helpers
├── templates/             # Flask HTML templates
└── output/                # CSV output files
```

---

## Output Format

### Amazon CSV

| Column | Description |
|--------|-------------|
| title | Product name |
| price | Price in INR |
| rating | Star rating (e.g., 4.5) |
| reviews | Number of reviews |
| product_url | Link to product page |

### Naukri CSV

| Column | Description |
|--------|-------------|
| title | Job title |
| company | Company name |
| experience | Required experience |
| location | Job location |
| salary | Salary range (if available) |
| job_url | Link to job posting |
| posted | When the job was posted |

---

## Notes

- Scrapers run in non-headless mode (browser visible) to avoid bot detection
- Amazon and Naukri may block requests if used excessively
- For educational and testing purposes only
