## MODIFIED Requirements

### Requirement: Robust Data Fetching
The data fetching layer SHALL gracefully handle HTTP exceptions and parse errors without crashing the main thread, and MUST return predictable empty states when data is unavailable.

#### Scenario: API rate limit or proxy failure
- **WHEN** a request to fetch daily close prices or current prices fails due to network exceptions
- **THEN** the function catches `requests.exceptions.RequestException` and logs the error, then returns `None` instead of `[]` or raising an unhandled exception.

#### Scenario: Strategy engine receives empty data
- **WHEN** the strategy engine calls a data-fetching function and receives `None`
- **THEN** the engine SHALL gracefully skip the current evaluation cycle for that symbol without crashing or raising an error.
