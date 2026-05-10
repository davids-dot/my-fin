## 1. Database & Model Updates

- [x] 1.1 Add `pe`, `market_cap`, and `industry` columns to `sql/sqlite/01_init_tables.sql`.
- [x] 1.2 Update `src/state/models.py` to include fundamental fields in the `StockList` class.

## 2. Data Ingestion & Sync

- [x] 2.1 Update `src/scripts/init_history.py` to parse and store PE, Market Cap, and Industry during the initial stock list fetch.
- [x] 2.2 Update `src/strategy/screener.py` to sync fundamental data from `ak.stock_zh_a_spot_em()` during the daily incremental update.

## 3. Screener Logic Enhancement

- [x] 3.1 Modify the SQL query in `src/strategy/screener.py` to JOIN `stock_list` and apply fundamental filters (e.g., PE and Market Cap thresholds).
- [x] 3.2 Add configuration parameters in `src/config.py` for fundamental screening thresholds (e.g., `MAX_PE`, `MIN_MARKET_CAP`).

## 4. Verification

- [ ] 4.1 Run `init_history.py` (stock list only) to verify fundamental data is correctly populated in the database.
- [ ] 4.2 Run `screener.py` and verify that the generated `watch_list` only contains stocks meeting both fundamental and technical criteria.
