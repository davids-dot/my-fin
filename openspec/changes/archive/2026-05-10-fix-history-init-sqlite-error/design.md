## Context

The system initializes history data for 5000+ A-share stocks. Each stock might have thousands of daily trading records. SQLite has a strict limit on the maximum number of host parameters in a single SQL statement. When attempting to `INSERT ... ON CONFLICT DO NOTHING` a large list of dictionaries using SQLAlchemy, it hits this limit, causing an `OperationalError`. Additionally, the main script retries all `Exception` classes generically. This results in the script uselessly retrying deterministic errors like database constraints or variable limits.

## Goals / Non-Goals

**Goals:**
- Prevent SQLite variable limit errors during bulk inserts without altering the database schema.
- Stop pointless retries on non-transient, deterministic errors to fail fast.
- Ensure all refactored functions in `init_history.py` remain strictly under 50 lines.

**Non-Goals:**
- Optimizing API download speed beyond what the provider allows.
- Switching away from SQLite to another database in this specific change.

## Decisions

**1. Chunking in `_fetch_and_save_daily`**
Instead of inserting the entire `records` list at once, we will slice the list into chunks of 100 records each.
- *Rationale*: SQLite's variable limit per statement is typically 999 (older versions) or 32766 (newer versions). 100 records * 8 columns = 800 variables, which safely avoids even the strictest 999 limit.
- *Alternative considered*: Updating the SQLite library or changing the connection string to allow more variables. This is environment-dependent and not portable.

**2. Differentiated Error Handling in `init_historical_daily`**
We will catch `sqlalchemy.exc.SQLAlchemyError` specifically and abort the retry loop.
- *Rationale*: SQLAlchemy errors (like `OperationalError`, `IntegrityError`) are almost always deterministic (e.g., schema mismatch, variable limits). Retrying them won't fix them. We should log the error and break out of the retry loop.
- *Alternative considered*: Catching `sqlite3.OperationalError` directly. However, SQLAlchemy wraps DBAPI errors, so catching `SQLAlchemyError` is more robust and ORM-agnostic.

## Risks / Trade-offs

- **Risk: Smaller chunk sizes increase the number of `execute` calls.**
  - *Mitigation*: We are doing this within a single transaction (`session.commit()` at the end of all chunks for a stock), so the I/O overhead is minimal.
- **Risk: Catching `SQLAlchemyError` might skip transient database locks.**
  - *Mitigation*: SQLite locks (`database is locked`) are technically `OperationalError`, but since this is an offline initialization script running serially, lock contention is highly unlikely.
