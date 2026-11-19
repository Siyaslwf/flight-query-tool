"""
Running queries against the flight database.
Student: Mohammed Siyas Chittakathu Kannankalil (251ADB014)
"""
import math
import re
from datetime import datetime

ALLOWED_KEYS = {
    "flight_id", "origin", "destination",
    "departure_datetime", "arrival_datetime",
    "price", "min_price", "sort_by", "order", "limit"
}

RECORD_FIELDS = {
    "flight_id", "origin", "destination",
    "departure_datetime", "arrival_datetime", "price"
}


def _valid_query(q: dict) -> bool:
    """Validate query keys, data types, and datetime formats."""
    if not isinstance(q, dict):
        return False

    # reject any unknown key
    for key in q:
        if key not in ALLOWED_KEYS:
            return False

    # exact-match string fields
    for field in ("flight_id", "origin", "destination"):
        if field in q and not isinstance(q[field], str):
            return False

    # datetime bounds (must be strict YYYY-MM-DD HH:MM)
    for dt_key in ("departure_datetime", "arrival_datetime"):
        if dt_key in q:
            val = q[dt_key]
            if not isinstance(val, str) or len(val) != 16:
                return False
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", val):
                return False
            try:
                datetime.strptime(val, "%Y-%m-%d %H:%M")
            except ValueError:
                return False

    # price bounds (must be int or float, NOT bool, and finite)
    for price_key in ("price", "min_price"):
        if price_key in q:
            val = q[price_key]
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                return False
            if math.isnan(val) or math.isinf(val):
                return False

    # sorting checks
    if "sort_by" in q:
        if not isinstance(q["sort_by"], str) or q["sort_by"] not in RECORD_FIELDS:
            return False

    if "order" in q:
        if "sort_by" not in q or q["order"] not in ("asc", "desc"):
            return False

    # limit check (integer >= 0, NOT bool)
    if "limit" in q:
        lim = q["limit"]
        if isinstance(lim, bool) or not isinstance(lim, int) or lim < 0:
            return False

    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object."""
    if not _valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = []
    for flight in db:
        if "flight_id" in query and flight["flight_id"] != query["flight_id"]:
            continue
        if "origin" in query and flight["origin"] != query["origin"]:
            continue
        if "destination" in query and flight["destination"] != query["destination"]:
            continue
        if "departure_datetime" in query and flight["departure_datetime"] < query["departure_datetime"]:
            continue
        if "arrival_datetime" in query and flight["arrival_datetime"] > query["arrival_datetime"]:
            continue
        if "price" in query and flight["price"] > query["price"]:
            continue
        if "min_price" in query and flight["price"] < query["min_price"]:
            continue
        matches.append(flight)

    # sort if requested
    if "sort_by" in query:
        sort_key = query["sort_by"]
        is_desc = query.get("order") == "desc"
        matches = sorted(matches, key=lambda f: f[sort_key], reverse=is_desc)

    # apply limit if requested
    if "limit" in query:
        matches = matches[: query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, dict):
        queries = [queries]
    return [run_query(db, q) for q in queries]

    