## Why

The current system only supports monitoring a hardcoded list of single stocks. To evolve into a true quantitative trading system, we need the capability to screen the entire A-share market daily, maintain a local history of stock prices for strategy evaluation, and automatically generate a dynamic watchlist for intraday monitoring. This change transitions the architecture from a simple single-stock watcher to a full "Data Warehouse + Screener + Monitor" pipeline.

## What Changes

- **BREAKING**: Re-architect the database to include `stock_list` (all A-shares), `stock_daily` (raw daily price history), and `watch_list` (dynamic daily targets).
- **BREAKING**: Move database schema definitions from SQLAlchemy ORM declarative models to explicit SQL files in the `sql/` directory.
- Introduce a dual-pipeline architecture: an offline daily screener (for populating the watchlist) and an intraday real-time monitor.
- Implement an initialization script to fetch full historical data for all A-shares.

## Capabilities

### New Capabilities
- `market-screener`: The ability to fetch whole-market daily data, store it locally, and execute strategies to generate a dynamic watchlist.
- `database-schema-management`: Explicit management of database schemas via pure SQL files instead of ORM auto-creation.

### Modified Capabilities
- `market-data-fetching`: Modified to support both full historical bulk fetching and daily incremental fetching.

## Impact

- **Affected Code**: `src/state/models.py`, `src/state/db.py`, `src/main.py`, `src/strategy/trend.py`.
- **New Folders/Files**: `sql/sqlite/`, `src/scripts/init_history.py`.
- **Dependencies**: No new external packages, but heavy reliance on AkShare's historical data APIs.
- **Systems**: The SQLite database `positions.db` will grow significantly due to storing daily historical prices for ~5000 stocks.
