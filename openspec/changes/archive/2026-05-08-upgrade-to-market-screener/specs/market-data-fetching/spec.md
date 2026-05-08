## MODIFIED Requirements

### Requirement: Robust Data Fetching
The data fetching layer SHALL gracefully handle HTTP exceptions and parse errors without crashing the main thread, MUST return predictable empty states when data is unavailable, and SHALL support both full history bulk fetches and incremental daily fetches for raw unadjusted prices.

#### Scenario: API rate limit or proxy failure
- **WHEN** a request to fetch daily close prices or current prices fails due to network exceptions
- **THEN** the function catches `requests.exceptions.RequestException` and logs the error, then returns `None` instead of `[]` or raising an unhandled exception.

#### Scenario: Strategy engine receives empty data
- **WHEN** the strategy engine calls a data-fetching function and receives `None`
- **THEN** the engine SHALL gracefully skip the current evaluation cycle for that symbol without crashing or raising an error.

#### Scenario: Initializing Historical Data
- **WHEN** the user manually triggers the `init_history` script
- **THEN** the system fetches raw (unadjusted) historical daily data for all active A-shares and populates the `stock_daily` table without duplicating existing records.

#### Scenario: Incremental Daily Update
- **WHEN** the daily screener task starts
- **THEN** the system fetches only the current day's raw daily data for all A-shares and inserts it into the `stock_daily` table.
