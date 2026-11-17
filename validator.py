"""Row validation: airport list loading, single-row checks, record building.

Student: Mohammed Siyas Chittakathu Kannankalil (251ADB014)

"""

import math
import re
from datetime import datetime


def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes."""
    airports = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            clean = line.strip()
            if clean and not clean.startswith("#"):
                airports.add(clean)
    return airports


def _valid_datetime(date_str: str) -> bool:
    """Helper to check strict YYYY-MM-DD HH:MM format and valid calendar time."""
    if len(date_str) != 16:
        return False
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", date_str):
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row against checks 1-11 in exact priority order."""
    # Check 1: exactly 6 fields required
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    clean_fields = [f.strip() for f in fields]
# Check 2: no field can be empty
    if any(val == "" for val in clean_fields):
        return "MISSING_FIELD"

    flight_id, origin, destination, dep_str, arr_str, price_str = clean_fields

    if not re.fullmatch(r"[A-Za-z0-9]{2,8}", flight_id):
        return "INVALID_FLIGHT_ID"

    if not re.fullmatch(r"[A-Z]{3}", origin) or origin not in airports:
        return "INVALID_ORIGIN"

    if not re.fullmatch(r"[A-Z]{3}", destination) or destination not in airports:
        return "INVALID_DESTINATION"

    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    if not _valid_datetime(dep_str):
        return "INVALID_DEPARTURE"

    if not _valid_datetime(arr_str):
        return "INVALID_ARRIVAL"

    dep_dt = datetime.strptime(dep_str, "%Y-%m-%d %H:%M")
    arr_dt = datetime.strptime(arr_str, "%Y-%m-%d %H:%M")
    if arr_dt <= dep_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price_num = float(price_str)
        if math.isnan(price_num) or math.isinf(price_num):
            return "INVALID_PRICE"
    except ValueError:
        return "INVALID_PRICE"

    if price_num <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary."""
    clean = [f.strip() for f in fields]
    return {
        "flight_id": clean[0],
        "origin": clean[1],
        "destination": clean[2],
        "departure_datetime": clean[3],
        "arrival_datetime": clean[4],
        "price": float(clean[5]),
    }
    