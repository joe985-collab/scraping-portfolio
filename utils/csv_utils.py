"""CSV utilities for reading, writing, and appending CSV files."""

import csv
import os
from typing import List, Dict, Any
from datetime import datetime


def generate_filename(prefix: str, query: str) -> str:
    """Generate a timestamped filename.

    Args:
        prefix: The prefix for the filename (e.g., 'amazon', 'naukri')
        query: The search query to include in filename

    Returns:
        Formatted filename like 'amazon_wireless_mouse_20240115_143022.csv'
    """
    safe_query = query.strip().replace(' ', '_').lower()[:30]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{safe_query}_{timestamp}.csv"


def write_csv(filepath: str, data: List[Dict[str, Any]], fieldnames: List[str] = None) -> bool:
    """Write data to a CSV file with headers.

    Args:
        filepath: Path to the CSV file
        data: List of dictionaries to write
        fieldnames: Optional list of field names. If not provided, extracted from first row.

    Returns:
        True if successful, False otherwise
    """
    if not data:
        return False

    if fieldnames is None:
        fieldnames = list(data[0].keys())

    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        return True
    except (IOError, OSError) as e:
        print(f"Error writing CSV: {e}")
        return False


def append_csv(filepath: str, data: List[Dict[str, Any]], fieldnames: List[str] = None) -> bool:
    """Append data to an existing CSV file or create new one.

    Args:
        filepath: Path to the CSV file
        data: List of dictionaries to append
        fieldnames: Optional list of field names

    Returns:
        True if successful, False otherwise
    """
    if not data:
        return False

    if fieldnames is None:
        fieldnames = list(data[0].keys())

    file_exists = os.path.exists(filepath)

    try:
        with open(filepath, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerows(data)
        return True
    except (IOError, OSError) as e:
        print(f"Error appending to CSV: {e}")
        return False


def load_csv(filepath: str) -> List[Dict[str, Any]]:
    """Load CSV file and return as list of dictionaries.

    Args:
        filepath: Path to the CSV file

    Returns:
        List of dictionaries representing each row, empty list if file not found
    """
    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except (IOError, OSError, csv.Error) as e:
        print(f"Error loading CSV: {e}")
        return []
