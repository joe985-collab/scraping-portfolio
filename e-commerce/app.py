from flask import Flask, render_template, jsonify, Response, request
import json
import csv
import io
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = 'first_page_product.json'

def load_products():
    """Load products from JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

@app.route('/')
def index():
    """Main page with product table."""
    products = load_products()
    return render_template('index.html', products=products)

@app.route('/api/products')
def get_products():
    """API endpoint to get all products."""
    products = load_products()
    return jsonify(products)

@app.route('/download/csv')
def download_csv():
    """Generate and download CSV file."""
    products = load_products()

    if not products:
        return "No data available", 404

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['name', 'price', 'mrp', 'rating', 'url'])
    writer.writeheader()
    writer.writerows(products)

    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=products_{timestamp}.csv'}
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)
