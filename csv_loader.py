"""Reading CSV files into flight records and error messages."""
import csv
import os

from validator import to_record, validate_row


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
    """
    records: list[dict] = []
    errors: list[str] = []
    # track (flight_id, departure_datetime) to catch duplicates across files
    seen_flights: set[tuple[str, str]] = set()

    for file_path in paths:
        file_name = os.path.basename(file_path)

        with open(file_path, "r", encoding="utf-8", newline="") as f:
            for line_num, raw_line in enumerate(f, start=1):
                line_text = raw_line.strip()

                # skip header line, empty lines, and comments
                if line_num == 1:
                    continue
                if not line_text or line_text.startswith("#"):
                    continue

                # parse single line with csv module
                row = next(csv.reader([raw_line.rstrip("\r\n")]), [])

                # run validation checks 1-11
                err_code = validate_row(row, airports)
                if err_code is not None:
                    errors.append(f"{file_name}:{line_num}: {err_code} | {line_text}")
                    continue

                # convert valid row and run check 12 (duplicate flight)
                flight_rec = to_record(row)
                flight_key = (flight_rec["flight_id"], flight_rec["departure_datetime"])

                if flight_key in seen_flights:
                    errors.append(f"{file_name}:{line_num}: DUPLICATE_FLIGHT | {line_text}")
                    continue

                seen_flights.add(flight_key)
                records.append(flight_rec)

    return records, errors

    