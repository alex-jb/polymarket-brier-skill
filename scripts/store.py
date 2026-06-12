"""polymarket-brier — local persistence.

JSONL append-only, one file per kind:
  ~/.polybrier/forecasts.jsonl   one line per (market_slug, source, ts)
  ~/.polybrier/audit.jsonl       one line per (forecast_id, brier, resolved_ts)
  ~/.polybrier/digest-cache.json optional rendered output

Why JSONL: same shape as solo-founder-os reflections/eval logs, so
sfos-eval can audit polymarket-brier the same way it audits any other
skill — calibration of the calibration layer.
"""
from __future__ import annotations
import json
import os
import pathlib
import time
from datetime import datetime, timezone
from typing import Optional


HOME = pathlib.Path(os.environ.get("POLYBRIER_HOME", str(pathlib.Path.home() / ".polybrier")))
FORECASTS = HOME / "forecasts.jsonl"
AUDITS = HOME / "audit.jsonl"


def _ensure_dir() -> None:
    HOME.mkdir(parents=True, exist_ok=True)


def _short_id(seed: str) -> str:
    import hashlib
    return "fc_" + hashlib.blake2b(seed.encode(), digest_size=3).hexdigest()


def write_forecast(
    *,
    market_slug: str,
    market_question: str,
    market_yes_p: Optional[float],
    own_p: float,
    rationale: str,
    source: str = "skill:polymarket-brier",
    model: str = "",
) -> dict:
    """Append one row, return it."""
    _ensure_dir()
    ts = datetime.now(timezone.utc).isoformat()
    fid = _short_id(f"{market_slug}|{source}|{ts}")
    row = {
        "id": fid,
        "ts": ts,
        "market_slug": market_slug,
        "market_question": market_question[:200],
        "market_yes_p": market_yes_p,
        "own_p": own_p,
        "edge": (own_p - market_yes_p) if market_yes_p is not None else None,
        "rationale": rationale[:1000],
        "source": source,
        "model": model,
    }
    with FORECASTS.open("a") as f:
        f.write(json.dumps(row) + "\n")
    return row


def read_forecasts() -> list[dict]:
    if not FORECASTS.exists():
        return []
    rows = []
    with FORECASTS.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def write_audit(*, forecast_id: str, brier: float, resolved_outcome: str, resolved_ts: str) -> dict:
    """Append one audit row. Idempotency is the caller's job — call
    `read_audits` first to skip already-scored forecasts."""
    _ensure_dir()
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "forecast_id": forecast_id,
        "brier": brier,
        "resolved_outcome": resolved_outcome,  # "Yes" | "No"
        "resolved_ts": resolved_ts,
    }
    with AUDITS.open("a") as f:
        f.write(json.dumps(row) + "\n")
    return row


def read_audits() -> list[dict]:
    if not AUDITS.exists():
        return []
    rows = []
    with AUDITS.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def safe_mode() -> bool:
    """When True, the forecaster is forced to Sonnet (no Mythos retention)."""
    return os.environ.get("POLYBRIER_SAFE_MODE", "0") not in ("0", "", "false", "False")
