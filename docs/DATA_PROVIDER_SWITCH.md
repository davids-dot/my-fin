# Data Provider Switch Guide

Due to network restrictions, proxies, or WAFs (Web Application Firewalls), the default East Money (东方财富) data source may occasionally fail with `RemoteDisconnected` or `Connection aborted` errors. 

To ensure the system can still operate under these network conditions, we have introduced a fallback data provider: **Sina Finance (新浪财经)**.

## How to Switch Providers

The data provider is controlled by the `DATA_PROVIDER` environment variable.

1. Open your `.env` file (or set the environment variable directly).
2. Add or modify the `DATA_PROVIDER` key:

```bash
# Use Sina Finance (Fast, bypasses most anti-bot walls, but lacks deep fundamental data)
DATA_PROVIDER=sina

# Use East Money (Default, contains PE, Market Cap, and Industry, but stricter network checks)
# DATA_PROVIDER=em
```

## Differences Between Providers

| Feature | `em` (East Money) | `sina` (Sina Finance) |
| :--- | :--- | :--- |
| **Speed** | Slower (paginated requests) | Very Fast (single batch request) |
| **Network Stability** | Low (Strict WAF, blocks some proxies) | High (Tolerant of proxies) |
| **Fundamental Data** | **Yes** (PE, Market Cap, Industry) | **No** (These fields will be `NULL` in DB) |
| **Screener Impact** | Full multi-factor screening works | Fundamental filters (PE, Market Cap) are effectively bypassed |

*Note: When using `sina`, the fundamental fields in `stock_list` will be stored as `NULL`. Since the SQL screener uses `(s.pe IS NULL OR s.pe < :max_pe)`, the stocks will still pass the fundamental filter and fall back to purely technical screening (e.g., 2-day consecutive rise).*
