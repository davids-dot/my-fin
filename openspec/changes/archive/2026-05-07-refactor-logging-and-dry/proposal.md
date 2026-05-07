## Why

The current implementation uses standard `print` statements for tracking execution flow and relies on broad `except Exception` blocks, making it difficult to debug system-level issues or trace errors accurately. Additionally, there's duplicated string manipulation logic across data-fetching functions. This refactoring addresses these Python anti-patterns by introducing proper logging, precise exception handling, and DRY code structuring, significantly improving system maintainability and observability.

## What Changes

- Replace all `print` statements with standard Python `logging` module.
- Refactor `market.py` to catch specific exceptions (e.g., network errors, parsing errors) rather than broad `Exception` clauses.
- Extract duplicated string manipulation (`symbol[2:] if symbol.startswith(('sh', 'sz')) else symbol`) into a shared helper function `_extract_code()`.
- Standardize error return types in data fetching functions to return `None` upon failure instead of `[]` to ensure clear semantic boundaries.
- Update `strategy/trend.py` to handle `None` return values appropriately from data functions.

## Capabilities

### New Capabilities
- `system-observability`: Implement standard application logging for monitoring system state, data fetching, and strategy execution.

### Modified Capabilities
- `market-data-fetching`: Update data fetching layer to handle errors precisely and return consistent `None` types on failure.

## Impact

- **Affected Code**: `src/my_fin/data/market.py`, `src/my_fin/strategy/trend.py`, `src/my_fin/main.py`, `src/my_fin/notify/bark.py`.
- **Dependencies**: No new external dependencies required (uses built-in `logging`).
- **Systems**: Improves operational monitoring and debugging efficiency.
