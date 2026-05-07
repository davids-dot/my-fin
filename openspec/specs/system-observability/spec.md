## ADDED Requirements

### Requirement: Application Logging
The system SHALL use standard Python `logging` for outputting operational information, warnings, and errors instead of standard output `print` statements.

#### Scenario: Strategy execution
- **WHEN** the minute-level strategy scheduler triggers a job
- **THEN** the system logs an INFO level message indicating the start of the job

#### Scenario: Trade signal triggered
- **WHEN** a buy or sell signal is successfully evaluated and executed
- **THEN** the system logs an INFO level message detailing the action (buy/sell), symbol, and price

#### Scenario: External API failure
- **WHEN** fetching data from external APIs (like AkShare or Bark) encounters an exception
- **THEN** the system logs an ERROR level message that includes the stack trace (`exc_info=True`)
