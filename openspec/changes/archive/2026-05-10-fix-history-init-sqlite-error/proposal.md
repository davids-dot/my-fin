## Why

The current historical data initialization script (`init_history.py`) encounters a `sqlite3.OperationalError: too many SQL variables` when attempting to bulk insert decades of daily stock data in a single transaction. Furthermore, the generic retry logic inappropriately retries these deterministic database errors, wasting time and resources instead of failing fast or handling them gracefully.

## What Changes

- Add chunking logic to the historical data insertion process to avoid SQLite's variable limit.
- Refine the exception handling in the retry loop to only retry on transient errors (e.g., network or API issues) and fail fast on deterministic database errors (e.g., `SQLAlchemyError`).

## Capabilities

### New Capabilities
- `sqlite-chunked-insert`: Safely bulk insert large datasets into SQLite by chunking them into smaller batches.
- `targeted-retry-logic`: Differentiate between transient network/API errors (which should be retried) and deterministic database/code errors (which should fail fast).

### Modified Capabilities

## Impact

- `src/scripts/init_history.py` will be modified.
- Database insertions will become safer and more reliable.
- The script will fail faster on critical errors, improving the debugging experience and preventing useless API requests.
