## 1. Logging Setup

- [x] 1.1 Create centralized logging configuration in `src/my_fin/config.py` using Python's built-in `logging` module.
- [x] 1.2 Replace `print` statements in `src/my_fin/notify/bark.py` with the configured logger.
- [x] 1.3 Replace `print` statements in `src/my_fin/main.py` and `src/my_fin/strategy/trend.py` with the configured logger.

## 2. DRY Refactoring in Data Layer

- [x] 2.1 Implement `_extract_code(symbol: str) -> str` helper function in `src/my_fin/data/market.py`.
- [x] 2.2 Refactor `get_daily_close_prices` and `get_current_price` to utilize the `_extract_code` helper.

## 3. Exception Handling & Return Types

- [x] 3.1 Update exception handling in `src/my_fin/data/market.py` to catch specific exceptions (e.g., network errors, parsing errors) and log with `exc_info=True`.
- [x] 3.2 Standardize error return types in `get_daily_close_prices` to return `None` instead of `[]` upon failure.
- [x] 3.3 Update `run_strategy` in `src/my_fin/strategy/trend.py` to correctly handle `None` returns from data fetching functions.

## 4. Verification

- [x] 4.1 Run `cargo check`, `cargo test`, and `cargo fmt --all` (if applicable/configured in the environment, though this is a Python project, we will run `uv run python -m pytest` or equivalent if tests exist, or manually verify script execution).
- [x] 4.2 Verify script executes without errors and logs are formatted correctly.