# AI Usage Disclosure

<!--
Fill in this file before you submit. Submissions without it are not graded.
If you used no AI tools, delete everything below and write only:
No AI tools were used.
-->

## Tools used

- DeepSeek AI (web chat)

## Conversation links

- Link 1: https://chat.deepseek.com/share/53lgyzjiz42ydht1pk

## What I used them for

- I asked step-by-step questions to understand how to do the 11 validation checks in `validator.py` in the right order without using `isalnum()` or `isupper()` on non-ASCII letters.
- I got help figuring out how to skip comment lines (`#`) and blank lines in `csv_loader.py` while still keeping the real physical line numbers for `errors.log`.
- I needed help understanding why `argparse` was giving tracebacks or wrong exit codes, and how to close the `logging` handler in `try/finally` so running `main()` twice does not break the log file.
- I got step-by-step assistance building and fixing `query.py` and `flight_parser.py` until all 29 public tests passed.

## Which parts of the code were AI-generated or substantially AI-assisted

| File | Function or part | How (generated / modified / explained) |
| `validator.py` | `load_airports`, `validate_row`, `to_record` | Explained how to do regex and datetime checks; AI helped write the structure and I modified names/comments |
| `csv_loader.py` | `parse_files` | Explained physical line counting and duplicate flight set checking; code was written with AI guidance |
| `query.py` | `run_query`, `run_queries`, `_valid_query` | Written with AI assistance for query validation, filtering, `sort_by`, and `limit` |
| `flight_parser.py` | `main`, `_CleanArgParser` | Written with AI assistance for `argparse` exit codes (0, 1, 2) and logging cleanup |

## Key prompts

1. "i have a python assignment for my uni where i have to make a flight parser tool with 4 files validator.py csv_loader.py query.py flight_parser.py. can you help me understand how to do validator.py first and how to check the 11 errors in order"
2. "for csv_loader how do i count line numbers. because line 1 is header and there are comment lines starting with # and empty lines that we should skip but the line number in error log still has to count them"
3. "in flight_parser.py sir said if user gives wrong arguments or missing -a with -i it should exit with code 2 and if file not found exit code 1. and no python traceback only Error: to stderr. how to do that with argparse"

## What I changed or verified myself

- I created the repository, organized the `data/` and `tests/` folders properly, and set my own `STUDENT_ID`, `FIRST_NAME`, and `LAST_NAME` in `flight_parser.py`.
- I read through each module to understand how the checks, CSV line numbers, and query filters work, and verified that only standard Python 3.13 libraries are used.
- I ran `python tests/run_public_tests.py` and verified all 29/29 tests pass.