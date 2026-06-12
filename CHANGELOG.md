# Changelog

## v0.1.0 — 2026-06-12

Initial release.

- `polymarket.py`: stdlib-only gamma-api wrapper (fetch_market, fetch_event, search_markets, parse_yes_price, parse_resolution_state)
- `store.py`: JSONL forecast + audit persistence, safe-mode flag for Mythos-class fallback
- `forecast.py`: `/brier forecast <slug>` — Haiku probability estimate with anti-injection wrapping
- `audit.py`: `/brier audit [--since=Nd]` — Brier-score every resolved forecast
- `digest.py`: `/brier digest [--emit=html]` — per-source calibration table + open mispricings

Pairs with [Last30days](https://github.com/mvanhorn/last30days-skill) (which surfaces hot markets) and [council-diff](https://github.com/alex-jb/council-diff) (which decides product questions).
