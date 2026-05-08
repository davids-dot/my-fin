## Context

The current `my-fin` system was designed to monitor a predefined list of stocks. To scale up, the system must act as a data warehouse that stores the raw, unadjusted daily prices of all A-share stocks. This data will be used by an offline daily screener to generate a dynamic `watch_list`. The real-time intraday engine will then only monitor stocks present in the `watch_list` and the `positions` table. Furthermore, the database schema definition will shift from SQLAlchemy ORM declarative models to explicit SQLite files.

## Goals / Non-Goals

**Goals:**
- Implement a dual-pipeline architecture: Offline Daily Screener (15:30) and Intraday Monitor (09:30-15:00).
- Design and explicitly define four database tables in `sql/sqlite/`: `stock_list`, `stock_daily`, `watch_list`, and `positions`.
- Provide a manual initialization script to download historical raw daily data for all A-shares.
- Ensure the database initialization process reads directly from the SQL files.

**Non-Goals:**
- Implementing a complex factor calculation engine or backtesting framework.
- Handling price adjustments (backward/forward復权) in the database; we explicitly store **raw (unadjusted)** prices only.

## Decisions

**1. Raw Prices vs. Adjusted Prices**
We will store **raw (unadjusted)** prices in the `stock_daily` table.
- *Rationale*: Storing adjusted prices requires recalculating and updating the entire history of a stock every time a dividend or split occurs. Storing raw prices is append-only and immutable. (Note: The strategy logic must eventually account for price gaps caused by dividends, but for this iteration, we focus on raw data ingestion).

**2. Explicit SQL Schema Management**
We will create `sql/sqlite/01_init_tables.sql` containing the `CREATE TABLE` statements. `src/state/db.py` will read and execute this file during initialization instead of relying on `Base.metadata.create_all()`.
- *Rationale*: Provides a single source of truth for the database schema, making it easier to migrate to MySQL in the future or manually inspect the database structure.

**3. Watchlist Target Price**
The `watch_list` table will include a `target_buy_price` and a `status` ('PENDING', 'BOUGHT', 'EXPIRED').
- *Rationale*: Decouples the offline screener from the intraday monitor. The screener calculates the threshold condition (e.g., T+1 close price), and the intraday monitor simply checks if `current_price > target_buy_price`.

## Risks / Trade-offs

- **[Risk] Initial History Download Time** → Mitigation: The initialization script `init_history.py` will be a standalone, manually triggered process. It can take hours to download 5000+ stocks, but it only needs to be run once.
- **[Risk] Database Size** → Mitigation: SQLite can easily handle gigabytes of data. Indexing on `(symbol, trade_date)` will ensure fast query performance during the daily screening phase.
