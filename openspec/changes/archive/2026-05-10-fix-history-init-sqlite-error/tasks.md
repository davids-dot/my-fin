## 1. Implement Chunking in `_fetch_and_save_daily`

- [x] 1.1 In `src/scripts/init_history.py`, locate `_fetch_and_save_daily`.
- [x] 1.2 Modify the insertion logic to slice the `records` list into chunks of 100.
- [x] 1.3 Iterate over the chunks, executing `session.execute(stmt)` for each chunk.
- [x] 1.4 Ensure the entire function remains under 50 lines.

## 2. Refine Exception Handling in `init_historical_daily`

- [x] 2.1 In `src/scripts/init_history.py`, locate `init_historical_daily`.
- [x] 2.2 Import `SQLAlchemyError` from `sqlalchemy.exc` at the top of the file.
- [x] 2.3 Add a specific `except SQLAlchemyError as e:` block before the generic `except Exception as e:` block inside the retry loop.
- [x] 2.4 In the `SQLAlchemyError` block, log the error, rollback the session, and set `retry_count = max_retries` to abort retries.
- [x] 2.5 Ensure the entire function remains under 50 lines.
