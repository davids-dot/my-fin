## ADDED Requirements

### Requirement: Explicit SQL Schema Definition
The database schema SHALL be defined exclusively via raw SQL files located in `sql/sqlite/` rather than relying on ORM auto-generation.

#### Scenario: Database Initialization
- **WHEN** the system starts up and detects a missing or uninitialized database
- **THEN** the system reads `sql/sqlite/01_init_tables.sql` and executes the raw DDL statements to create the `stock_list`, `stock_daily`, `watch_list`, and `positions` tables.
