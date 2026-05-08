## ADDED Requirements

### Requirement: Daily Offline Screener
The system SHALL run a daily screener task after market close to evaluate strategies across the full A-share market history and populate a dynamic watchlist for the next trading day.

#### Scenario: Daily screening triggered
- **WHEN** the daily schedule is reached (e.g., 15:30)
- **THEN** the system fetches incremental daily data, evaluates the "2-day consecutive rise" strategy, and inserts qualifying stocks into the `watch_list` table with a 'PENDING' status and a calculated `target_buy_price`.

### Requirement: Watchlist-driven Intraday Monitor
The real-time intraday engine SHALL only monitor stocks present in the `watch_list` (with status 'PENDING') or currently held in the `positions` table.

#### Scenario: Intraday buy condition met
- **WHEN** a stock in the `watch_list` exceeds its `target_buy_price` during intraday monitoring
- **THEN** the system executes a buy, inserts a record into the `positions` table, updates the `watch_list` status to 'BOUGHT', and sends a notification.
