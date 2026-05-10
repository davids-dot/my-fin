## Context

The current `stock_list` table only contains basic identifiers (symbol, name, market). Our screening strategy is purely technical, making it susceptible to choosing stocks with poor fundamentals. We need to enrich our local data warehouse with valuation (PE), size (Market Cap), and categorization (Industry) data to enable a "Quality first, Trend second" screening pipeline.

## Goals / Non-Goals

**Goals:**
- Extend the SQLite schema to store fundamental data.
- Enhance data ingestion to pull these fields from AkShare.
- Implement a multi-factor query in the screener to filter by fundamental thresholds.

**Non-Goals:**
- Storing full historical fundamental data (only current snapshots are needed for screening).
- Real-time fundamental updates (daily updates at 15:30 are sufficient).

## Decisions

**1. Data Source: `ak.stock_zh_a_spot_em()`**
We will use the existing `stock_zh_a_spot_em()` interface for daily fundamental updates.
- *Rationale*: This interface already provides `市盈率-动态` (PE), `总市值` (Market Cap), and `板块` (Industry) in a single call, avoiding the need for multiple API hits per stock.

**2. Storage Strategy: Snapshot in `stock_list`**
Fundamental data will be stored as columns in the `stock_list` table rather than a separate time-series table.
- *Rationale*: Fundamental values for screening (like Industry or PE) change relatively slowly compared to prices. A daily snapshot in the main list table simplifies SQL joins in the screener.

**3. Flexible Filtering via SQL**
The screener will use a configurable SQL `WHERE` clause to apply fundamental filters.
- *Rationale*: Allows easy adjustment of parameters (e.g., "Market Cap > 50 Billion") without changing the Python application logic.

## Risks / Trade-offs

- **[Risk] Missing Data** → Mitigation: Use `NULL` for missing fields and ensure the SQL screener handles null values gracefully (e.g., using `COALESCE` or simple exclusion).
- **[Risk] PE Fluctuations** → Mitigation: Recognize that dynamic PE changes with price; we update this daily to ensure the screener uses the most recent valuation.
