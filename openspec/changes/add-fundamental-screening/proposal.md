## Why

The current market screener only relies on technical indicators (consecutive price rises). To improve the quality of the watchlist and reduce the risk of selecting financially unstable stocks, we need to incorporate fundamental filters. This allows the system to focus on "high-quality" companies before applying technical entry signals.

## What Changes

- **Database Schema**: Add fundamental fields (`pe`, `pb`, `market_cap`, `industry`) to the `stock_list` table.
- **Data Ingestion**: Update `init_history.py` and create a daily synchronization logic to fetch fundamental data from AkShare.
- **Screener Logic**: Modify `screener.py` to include fundamental filters (e.g., market cap > X, PE < Y) in the SQL selection query.

## Capabilities

### New Capabilities
- `fundamental-analysis`: The ability to store, sync, and filter stocks based on company financial indicators like PE, market capitalization, and industry sector.

### Modified Capabilities
- `market-screener`: The screening logic will be updated to support a multi-factor approach (Fundamental + Technical).

## Impact

- **Affected Code**: `sql/sqlite/01_init_tables.sql`, `src/state/models.py`, `src/scripts/init_history.py`, `src/strategy/screener.py`.
- **APIs**: Enhanced use of `ak.stock_zh_a_spot_em()` to extract additional valuation and industry fields.
- **Database**: `stock_list` table will be expanded with new columns.
