"""Deduplication utilities for scraped data."""

from typing import List, Dict, Any


def deduplicate_by_key(data: List[Dict[str, Any]], key: str) -> List[Dict[str, Any]]:
    """Deduplicate a list of dictionaries by a specific key.

    Keeps the first occurrence of each unique key value.

    Args:
        data: List of dictionaries to deduplicate
        key: The dictionary key to use for deduplication

    Returns:
        Deduplicated list with first occurrences preserved
    """
    if not data:
        return []

    seen = set()
    result = []

    for item in data:
        value = item.get(key)
        if value is None:
            # Keep items with missing key values
            result.append(item)
        elif value not in seen:
            seen.add(value)
            result.append(item)

    return result


def deduplicate_csv_file(filepath: str, key: str) -> int:
    """Deduplicate a CSV file in place by a specific key.

    Args:
        filepath: Path to the CSV file
        key: The column to use for deduplication

    Returns:
        Number of duplicates removed
    """
    from .csv_utils import load_csv, write_csv

    data = load_csv(filepath)
    if not data:
        return 0

    original_count = len(data)
    deduped = deduplicate_by_key(data, key)

    if len(deduped) < original_count:
        fieldnames = list(data[0].keys())
        write_csv(filepath, deduped, fieldnames)

    return original_count - len(deduped)
