"""Unified Flask application for Amazon and Naukri scrapers."""

import os
import threading
from flask import Flask, render_template, request, redirect, url_for, send_file, flash

from utils.csv_utils import load_csv
from scrapers.amazon_scraper import scrape_amazon
from scrapers.naukri_scraper import scrape_naukri

app = Flask(__name__)
app.secret_key = os.urandom(24)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')

# Track running scraper tasks
scraper_status = {
    'amazon': {'running': False, 'filename': None, 'error': None},
    'naukri': {'running': False, 'filename': None, 'error': None}
}


def run_amazon_scraper(query: str, max_pages: int):
    """Run Amazon scraper in background thread."""
    global scraper_status
    try:
        scraper_status['amazon']['error'] = None
        result = scrape_amazon(query, max_pages, OUTPUT_DIR)
        if result:
            scraper_status['amazon']['filename'] = os.path.basename(result)
        else:
            scraper_status['amazon']['error'] = 'No products found or scraping failed'
    except Exception as e:
        scraper_status['amazon']['error'] = str(e)
    finally:
        scraper_status['amazon']['running'] = False


def run_naukri_scraper(keyword: str, location: str, max_pages: int):
    """Run Naukri scraper in background thread."""
    global scraper_status
    try:
        scraper_status['naukri']['error'] = None
        result = scrape_naukri(keyword, location, max_pages, OUTPUT_DIR)
        if result:
            scraper_status['naukri']['filename'] = os.path.basename(result)
        else:
            scraper_status['naukri']['error'] = 'No jobs found or scraping failed'
    except Exception as e:
        scraper_status['naukri']['error'] = str(e)
    finally:
        scraper_status['naukri']['running'] = False


@app.route('/')
def index():
    """Home page with links to both scrapers."""
    return render_template('index.html')


# ============== Amazon Routes ==============

@app.route('/amazon')
def amazon_home():
    """Amazon scraper search page."""
    status = scraper_status['amazon'].copy()
    return render_template('amazon.html', status=status)


@app.route('/amazon/search', methods=['POST'])
def amazon_search():
    """Start Amazon product search."""
    if scraper_status['amazon']['running']:
        flash('A scraper is already running. Please wait.', 'warning')
        return redirect(url_for('amazon_home'))

    query = request.form.get('query', '').strip()
    max_pages = int(request.form.get('max_pages', 5))

    if not query:
        flash('Please enter a search query.', 'error')
        return redirect(url_for('amazon_home'))

    # Start scraper in background thread
    scraper_status['amazon']['running'] = True
    scraper_status['amazon']['filename'] = None
    thread = threading.Thread(target=run_amazon_scraper, args=(query, max_pages))
    thread.daemon = True
    thread.start()

    flash(f'Started scraping Amazon for "{query}". Please wait...', 'info')
    return redirect(url_for('amazon_home'))


@app.route('/amazon/status')
def amazon_status():
    """Check Amazon scraper status (for AJAX polling)."""
    from flask import jsonify
    return jsonify(scraper_status['amazon'])


@app.route('/amazon/results/<filename>')
def amazon_results(filename):
    """Display Amazon scraping results."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        flash('Results file not found.', 'error')
        return redirect(url_for('amazon_home'))

    data = load_csv(filepath)
    return render_template('amazon_results.html', products=data, filename=filename)


@app.route('/amazon/download/<filename>')
def amazon_download(filename):
    """Download Amazon CSV file."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        flash('File not found.', 'error')
        return redirect(url_for('amazon_home'))

    return send_file(filepath, as_attachment=True, download_name=filename)


# ============== Naukri Routes ==============

@app.route('/naukri')
def naukri_home():
    """Naukri scraper search page."""
    status = scraper_status['naukri'].copy()
    return render_template('naukri.html', status=status)


@app.route('/naukri/search', methods=['POST'])
def naukri_search():
    """Start Naukri job search."""
    if scraper_status['naukri']['running']:
        flash('A scraper is already running. Please wait.', 'warning')
        return redirect(url_for('naukri_home'))

    keyword = request.form.get('keyword', '').strip()
    location = request.form.get('location', '').strip()
    max_pages = int(request.form.get('max_pages', 5))

    if not keyword:
        flash('Please enter a job keyword.', 'error')
        return redirect(url_for('naukri_home'))

    # Start scraper in background thread
    scraper_status['naukri']['running'] = True
    scraper_status['naukri']['filename'] = None
    thread = threading.Thread(target=run_naukri_scraper, args=(keyword, location, max_pages))
    thread.daemon = True
    thread.start()

    flash(f'Started scraping Naukri for "{keyword}". Please wait...', 'info')
    return redirect(url_for('naukri_home'))


@app.route('/naukri/status')
def naukri_status():
    """Check Naukri scraper status (for AJAX polling)."""
    from flask import jsonify
    return jsonify(scraper_status['naukri'])


@app.route('/naukri/results/<filename>')
def naukri_results(filename):
    """Display Naukri scraping results."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        flash('Results file not found.', 'error')
        return redirect(url_for('naukri_home'))

    data = load_csv(filepath)
    return render_template('naukri_results.html', jobs=data, filename=filename)


@app.route('/naukri/download/<filename>')
def naukri_download(filename):
    """Download Naukri CSV file."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        flash('File not found.', 'error')
        return redirect(url_for('naukri_home'))

    return send_file(filepath, as_attachment=True, download_name=filename)


if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(debug=True, port=5000)
