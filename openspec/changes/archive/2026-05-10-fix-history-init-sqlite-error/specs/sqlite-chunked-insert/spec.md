## ADDED Requirements

### Requirement: Bulk insert with chunking
The system SHALL insert historical daily records into the SQLite database in chunks of no more than 100 records per batch to avoid exceeding SQLite's maximum host parameter limit.

#### Scenario: Inserting a large list of records
- **WHEN** the system fetches a large dataset (e.g., 3000 daily records) for a single stock
- **THEN** the system slices the records into chunks of 100
- **THEN** the system executes the `insert().on_conflict_do_nothing()` statement for each chunk separately
- **THEN** all chunks for the single stock are committed in a single database transaction

#### Scenario: Inserting a small list of records
- **WHEN** the system fetches a small dataset (e.g., 50 daily records)
- **THEN** the system processes it as a single chunk
- **THEN** the chunk is executed and committed successfully
