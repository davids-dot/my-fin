## MODIFIED Requirements

### Requirement: Daily Offline Screener
The system SHALL run a daily screener task after market close to evaluate strategies across the full A-share market history and fundamental filters to populate a dynamic watchlist for the next trading day.

#### Scenario: Daily screening triggered with fundamental filters
- **WHEN** the daily schedule is reached (e.g., 15:30)
- **THEN** the system fetches incremental daily data, applies fundamental filters (e.g., PE < 50, Market Cap > 50B), evaluates the "2-day consecutive rise" strategy on the filtered set, and inserts qualifying stocks into the `watch_list` table.
