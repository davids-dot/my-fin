## ADDED Requirements

### Requirement: Fundamental Data Storage
The system SHALL store stock valuation and industry information including PE ratio, market capitalization, and industry sector in the local database.

#### Scenario: Database schema updated
- **WHEN** the database initialization script is executed
- **THEN** the `stock_list` table contains columns for `pe`, `market_cap`, and `industry`.

### Requirement: Fundamental Data Synchronization
The system SHALL synchronize fundamental data snapshots for all stocks in the `stock_list` on a daily basis.

#### Scenario: Daily fundamental sync
- **WHEN** the post-market sync task is triggered
- **THEN** the system fetches PE, market cap, and industry data from AkShare and updates the corresponding records in the `stock_list` table.
