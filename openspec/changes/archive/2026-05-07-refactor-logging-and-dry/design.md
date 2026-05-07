## Context

The current `my-fin` application relies on `print` statements for tracking strategy execution and broad `Exception` blocks for error handling. This limits observability in production environments, making it difficult to pinpoint root causes (e.g., distinguishing between a network timeout, a rate limit, or an unexpected data format). Additionally, the AkShare data integration layer contains duplicated logic for normalizing symbol prefixes (`sh`, `sz`), violating DRY principles. As we move towards a more robust production-ready state, implementing proper Python patterns is essential.

## Goals / Non-Goals

**Goals:**
- Implement structured application logging using Python's built-in `logging` module.
- Refactor `market.py` to catch specific exceptions (e.g., `requests.exceptions.RequestException`, `urllib3.exceptions.HTTPError`).
- Extract the symbol normalization logic into a helper function to enforce DRY principles.
- Standardize the error return types of data-fetching functions to `None`.

**Non-Goals:**
- Introducing external logging frameworks like `loguru` or integrating with third-party log aggregation services (ELK/Datadog) at this stage.
- Modifying the core trading strategy logic, other than adapting to the new `None` return types.

## Decisions

**1. Centralized Logging Configuration**
We will configure logging centrally in `src/my_fin/config.py` or via a dedicated `logger.py` module. It will use a standard format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s` to ensure consistency.
- *Alternative Considered*: Ad-hoc logging setup in each module. Rejected because it leads to inconsistent log formats and difficult log level management.

**2. Specific Exception Handling**
We will use the `requests.exceptions.RequestException` for network-level issues and `KeyError`/`ValueError` for DataFrame parsing issues in `market.py`.
- *Alternative Considered*: Keeping `Exception` but logging the traceback. Rejected because it's a Python anti-pattern and doesn't allow for specific recovery strategies per error type.

**3. Shared Symbol Extractor**
A private helper `_extract_code(symbol: str) -> str` will be created in `market.py` to handle the `sh`/`sz` stripping logic.

## Risks / Trade-offs

- **[Risk] Existing Strategy Breaks on `None` Returns** → Mitigation: We must ensure that `strategy/trend.py` explicitly checks for `if closes is None:` or `if not closes:` and safely exits the current iteration without crashing or triggering false logic.
- **[Risk] Logging overhead** → Mitigation: Since the strategy runs on a minute-frequency and the log volume is small, the overhead of standard `logging` to standard output (or file) is negligible.
