"""polymarket-brier — gamma-api wrapper.

Stdlib only. One HTTP GET, one parse, no dependencies on the orallexa
stack so the skill installs cleanly anywhere `pip install` works.

Gamma-api shape (https://gamma-api.polymarket.com):
  /events?slug=<slug>   → {events: [{ id, slug, title, markets: [...] }]}
  /markets?slug=<slug>  → list[{ id, question, slug, outcomePrices: [str], volume, endDate }]

We default to /markets because it's what /brier forecast operates on.
"""
from __future__ import annotations
import json
import urllib.error
import urllib.request
from typing import Optional


GAMMA = "https://gamma-api.polymarket.com"


class PolymarketError(RuntimeError):
    pass


def _get(path: str, timeout: float = 10.0) -> object:
    url = f"{GAMMA}{path}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "polymarket-brier/0.1",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        raise PolymarketError(f"HTTP {e.code} on {path}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        raise PolymarketError(f"network: {e}") from e


def fetch_market(slug: str) -> Optional[dict]:
    """Return the market matching slug or None.

    Polymarket's gamma-api returns a list; filter to the exact slug match.
    The slug is unique so the list length is 0 or 1 in practice.
    """
    data = _get(f"/markets?slug={slug}&closed=false")
    if not isinstance(data, list):
        return None
    for m in data:
        if m.get("slug") == slug:
            return m
    return None


def fetch_event(slug: str) -> Optional[dict]:
    """Return the event (a multi-outcome bucket) matching slug or None."""
    data = _get(f"/events?slug={slug}")
    if not isinstance(data, list):
        return None
    for ev in data:
        if ev.get("slug") == slug:
            return ev
    return None


def search_markets(keyword: str, limit: int = 5) -> list[dict]:
    """Best-effort search by keyword over active markets, ranked by volume."""
    data = _get(f"/markets?active=true&closed=false&limit=50")
    if not isinstance(data, list):
        return []
    kw = keyword.lower()
    matches = [m for m in data if kw in (m.get("question") or "").lower()]
    matches.sort(key=lambda m: float(m.get("volume") or 0), reverse=True)
    return matches[:limit]


def parse_yes_price(market: dict) -> Optional[float]:
    """Extract the YES probability (0-1) from a gamma market row.

    gamma-api returns outcomePrices as a JSON-string of a list:
      "[\"0.62\", \"0.38\"]"  ← YES, NO
    """
    raw = market.get("outcomePrices")
    if not raw:
        return None
    try:
        prices = raw if isinstance(raw, list) else json.loads(raw)
        if not prices:
            return None
        return float(prices[0])
    except (json.JSONDecodeError, ValueError, TypeError):
        return None


def parse_resolution_state(market: dict) -> str:
    """Classify market state for the auditor.

    Returns: "open" | "resolved_yes" | "resolved_no" | "ambiguous"
    """
    if market.get("closed") and market.get("resolvedOutcome") == "Yes":
        return "resolved_yes"
    if market.get("closed") and market.get("resolvedOutcome") == "No":
        return "resolved_no"
    if market.get("closed"):
        return "ambiguous"
    return "open"
