"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import argparse
import json
import logging
import os
import sys
from datetime import datetime

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

STUDENT_ID = "251ADB014"
FIRST_NAME = "MohammedSiyas"
LAST_NAME = "ChittakathuKannankalil"


class _CleanArgParser(argparse.ArgumentParser):
    """Custom parser that prints a clean Error: message to stderr on usage errors."""

    def error(self, message):
        sys.stderr.write(f"Error: {message}\n")
        sys.exit(2)


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2)."""
    if argv is None:
        argv = sys.argv[1:]

    parser = _CleanArgParser(
        description="Flight Schedule Parser and Query Tool"
    )
    parser.add_argument("-i", dest="input_file", help="Parse a single CSV file")
    parser.add_argument("-d", dest="input_dir", help="Parse all .csv files in a folder")
    parser.add_argument("-j", dest="json_db", help="Load an existing JSON database")
    parser.add_argument("-a", dest="airports_file", help="Airport codes file")
    parser.add_argument("-o", dest="output_db", help="Output JSON database path")
    parser.add_argument("-q", dest="query_file", help="JSON query file")
    parser.add_argument("-r", dest="response_dir", default=".", help="Folder for response JSON")

    # Catch argparse SystemExit so main() returns the exit code directly
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    # Check data source rules: exactly one of -i, -d, or -j
    sources = [s for s in (args.input_file, args.input_dir, args.json_db) if s is not None]
    if len(sources) == 0:
        sys.stderr.write("Error: Exactly one data source (-i, -d, -j) is required\n")
        return 2
    if len(sources) > 1:
        sys.stderr.write("Error: Only one data source (-i, -d, -j) may be given\n")
        return 2

    # -a is required when using -i or -d
    if (args.input_file or args.input_dir) and not args.airports_file:
        sys.stderr.write("Error: -a airport list file is required with -i or -d\n")
        return 2

    # -o cannot be used with -j
    if args.json_db and args.output_db:
        sys.stderr.write("Error: -o is not allowed with -j\n")
        return 2

    db_out_path = args.output_db if args.output_db else "db.json"
    log_dir = os.path.dirname(db_out_path) or "."
    log_path = os.path.join(log_dir, "errors.log")

    logger = logging.getLogger("flight_parser")
    logger.setLevel(logging.INFO)
    handler = None

    try:
        db: list[dict] = []

        if args.input_file or args.input_dir:
            # Attach logging handler for errors.log
            handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            logger.addHandler(handler)

            # Read airport list
            if not os.path.isfile(args.airports_file):
                sys.stderr.write(f"Error: Airport file not found: {args.airports_file}\n")
                return 1
            try:
                airports = load_airports(args.airports_file)
            except Exception as err:
                sys.stderr.write(f"Error: Could not read airport file: {err}\n")
                return 1

            # Determine CSV file paths
            csv_paths: list[str] = []
            if args.input_file:
                if not os.path.isfile(args.input_file):
                    sys.stderr.write(f"Error: CSV file not found: {args.input_file}\n")
                    return 1
                csv_paths = [args.input_file]
            else:
                if not os.path.isdir(args.input_dir):
                    sys.stderr.write(f"Error: Folder not found: {args.input_dir}\n")
                    return 1
                csv_names = sorted(
                    [
                        name
                        for name in os.listdir(args.input_dir)
                        if name.endswith(".csv")
                        and os.path.isfile(os.path.join(args.input_dir, name))
                    ]
                )
                if not csv_names:
                    sys.stderr.write(f"Error: No .csv files found in folder: {args.input_dir}\n")
                    return 1
                csv_paths = [os.path.join(args.input_dir, name) for name in csv_names]

            # Parse CSV files and log warnings
            try:
                db, errors = parse_files(csv_paths, airports)
            except Exception as err:
                sys.stderr.write(f"Error: Failed to parse CSV files: {err}\n")
                return 1

            for msg in errors:
                logger.warning(msg)

            # Save parsed flights to JSON database
            try:
                with open(db_out_path, "w", encoding="utf-8") as f:
                    json.dump(db, f, indent=2)
            except Exception as err:
                sys.stderr.write(f"Error: Failed to write database JSON: {err}\n")
                return 1

        else:
            # Load existing JSON database (-j)
            if not os.path.isfile(args.json_db):
                sys.stderr.write(f"Error: JSON database not found: {args.json_db}\n")
                return 1
            try:
                with open(args.json_db, "r", encoding="utf-8") as f:
                    db = json.load(f)
                if not isinstance(db, list) or not all(isinstance(r, dict) for r in db):
                    sys.stderr.write("Error: JSON database must be an array of objects\n")
                    return 1
            except Exception as err:
                sys.stderr.write(f"Error: Invalid JSON database: {err}\n")
                return 1

        # Optional query execution (-q)
        if args.query_file:
            if not os.path.isfile(args.query_file):
                sys.stderr.write(f"Error: Query file not found: {args.query_file}\n")
                return 1
            try:
                with open(args.query_file, "r", encoding="utf-8") as f:
                    queries = json.load(f)
                if not isinstance(queries, (dict, list)):
                    sys.stderr.write("Error: Query file must be an object or array of objects\n")
                    return 1
            except Exception as err:
                sys.stderr.write(f"Error: Invalid query file: {err}\n")
                return 1

            results = run_queries(db, queries)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            resp_name = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp}.json"
            resp_path = os.path.join(args.response_dir, resp_name)

            try:
                with open(resp_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2)
            except Exception as err:
                sys.stderr.write(f"Error: Failed to write response file: {err}\n")
                return 1

        return 0

    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()


if __name__ == "__main__":
    sys.exit(main())


    