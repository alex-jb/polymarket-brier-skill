"""polymarket-brier — /brier audit

For every forecast whose market resolved since we last ran, compute
Brier score and append to audit.jsonl.

Brier = (own_p - actual)^2 where actual is 1 for YES resolution, 0 for NO.
Lower is better. Random forecasts → 0.25. Anything below 0.20 is real edge.
"""
from __future__ import annotations
import argparse
import sys
from datetime import datetime, timedelta, timezone

from polymarket import fetch_market, parse_resolution_state
from store import read_forecasts, read_audits, write_audit


def _is_too_old(ts_iso: str, since: timedelta | None) -> bool:
    if since is None:
        return False
    try:
        ts = datetime.fromisoformat(ts_iso.replace("Z", "+00:00"))
    except ValueError:
        return True
    return (datetime.now(timezone.utc) - ts) > since


def _parse_since(s: str | None) -> timedelta | None:
    if not s:
        return None
    s = s.strip().lower()
    if s.endswith("d"):
        return timedelta(days=int(s[:-1]))
    if s.endswith("h"):
        return timedelta(hours=int(s[:-1]))
    return None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--since", default=None,
                   help="Only consider forecasts written within this window (e.g. 7d, 24h)")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    since = _parse_since(args.since)
    forecasts = read_forecasts()
    audited_ids = {row["forecast_id"] for row in read_audits()}

    scored = 0
    for f in forecasts:
        if f["id"] in audited_ids:
            continue
        if _is_too_old(f["ts"], since):
            continue
        market = fetch_market(f["market_slug"])
        if market is None:
            continue
        state = parse_resolution_state(market)
        if state == "open":
            continue
        if state == "ambiguous":
            if not args.quiet:
                print(f"  ?  {f['id']} {f['market_slug']} resolved ambiguously, skipping")
            continue

        actual = 1.0 if state == "resolved_yes" else 0.0
        brier = (float(f["own_p"]) - actual) ** 2
        resolved_ts = market.get("endDate") or datetime.now(timezone.utc).isoformat()
        write_audit(
            forecast_id=f["id"],
            brier=brier,
            resolved_outcome=("Yes" if actual == 1.0 else "No"),
            resolved_ts=resolved_ts,
        )
        scored += 1
        if not args.quiet:
            mark = "✓" if brier < 0.25 else "✗"
            print(f"  {mark} {f['id']} brier={brier:.3f} source={f['source']}")

    print(f"\nAudited {scored} new forecast(s).")
    if scored > 0:
        print("Run `/brier digest` for the per-source calibration table.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
