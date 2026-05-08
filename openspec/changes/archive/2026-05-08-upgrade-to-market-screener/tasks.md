## 1. Database Schema Management

- [x] 1.1 Create `sql/sqlite/01_init_tables.sql` containing DDL for `stock_list`, `stock_daily`, `watch_list`, and `positions`.
- [x] 1.2 Update `src/state/db.py` to read and execute the SQL file during initialization instead of using SQLAlchemy's `create_all()`.
- [x] 1.3 Update `src/state/models.py` to reflect the new tables (`StockList`, `StockDaily`, `WatchList`) so SQLAlchemy can still query them.

## 2. Data Fetching & Initialization

- [x] 2.1 Create `src/scripts/init_history.py` to fetch the full A-share stock list and insert into `stock_list`.
- [x] 2.2 Update `init_history.py` to iterate over `stock_list` and fetch raw historical daily data into `stock_daily`.
- [x] 2.3 Update `src/data/market.py` to support fetching incremental daily raw data for a given date.

## 3. Dual Pipeline Implementation

- [x] 3.1 Create `src/strategy/screener.py` (Daily Screener) to run at 15:30: fetch incremental daily data, evaluate the strategy, and populate the `watch_list`.
- [x] 3.2 Update `src/strategy/trend.py` (Intraday Monitor) to only monitor symbols present in `watch_list` (PENDING) and `positions`.
- [x] 3.3 Update `src/main.py` to configure APScheduler with two distinct jobs: the intraday monitor (09:30-15:00) and the daily screener (15:30).

## 4. Verification

- [x] 4.1 Run the database initialization and verify tables are created correctly.
- [x] 4.2 Execute a dry-run of the intraday monitor and verify it reads from the correct tables without errors.