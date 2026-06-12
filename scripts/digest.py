"""polymarket-brier — /brier digest

Render the current calibration state as Markdown:
  - Per-source Brier (mean + n) sorted ascending (best first)
  - Top mispricings still open (|own_p - market_p| > threshold)
  - Recent forecasts (last 10)

Optional --emit=html writes a standalone dark-mode page.
"""
from __future__ import annotations
import argparse
import os
import statistics
import sys
from datetime import datetime, timezone

from store import read_forecasts, read_audits


def per_source_brier() -> list[dict]:
    forecasts = {f["id"]: f for f in read_forecasts()}
    by_source: dict[str, list[float]] = {}
    for a in read_audits():
        fid = a["forecast_id"]
        if fid not in forecasts:
            continue
        src = forecasts[fid]["source"]
        by_source.setdefault(src, []).append(a["brier"])
    out = []
    for src, briers in by_source.items():
        out.append({
            "source": src,
            "n": len(briers),
            "mean": statistics.fmean(briers),
            "median": statistics.median(briers),
        })
    out.sort(key=lambda r: r["mean"])
    return out


def open_mispricings(threshold: float = 0.05) -> list[dict]:
    out = []
    audited = {a["forecast_id"] for a in read_audits()}
    for f in read_forecasts():
        if f["id"] in audited:
            continue
        if f.get("market_yes_p") is None or f.get("edge") is None:
            continue
        if abs(f["edge"]) >= threshold:
            out.append(f)
    out.sort(key=lambda r: abs(r["edge"]), reverse=True)
    return out


def render_markdown() -> str:
    ts = datetime.now(timezone.utc).isoformat()
    parts = [
        f"# polymarket-brier — calibration digest",
        f"_{ts}_",
        "",
        "## Calibration per source",
        "",
        "| source | n | mean Brier | median |",
        "|---|---|---|---|",
    ]
    rows = per_source_brier()
    if not rows:
        parts.append("| _no audits yet — run `/brier audit`_ | 0 | — | — |")
    else:
        for r in rows:
            edge_tag = ""
            if r["mean"] < 0.20:
                edge_tag = " 🟢"
            elif r["mean"] > 0.30:
                edge_tag = " 🔴"
            parts.append(f"| `{r['source']}` | {r['n']} | {r['mean']:.3f}{edge_tag} | {r['median']:.3f} |")

    parts += ["", "## Open mispricings (|edge| ≥ 5%)", ""]
    mis = open_mispricings(0.05)[:10]
    if not mis:
        parts.append("_None — every persisted forecast is within 5% of the market._")
    else:
        parts += ["| slug | market_p | ours_p | edge | source |", "|---|---|---|---|---|"]
        for m in mis:
            mp = m["market_yes_p"]
            op = m["own_p"]
            edge = m["edge"]
            parts.append(
                f"| `{m['market_slug']}` | {mp:.2f} | {op:.2f} | {edge:+.2f} | `{m['source']}` |"
            )

    return "\n".join(parts) + "\n"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--emit", choices=["markdown", "html"], default="markdown")
    args = p.parse_args()
    md = render_markdown()
    if args.emit == "markdown":
        print(md)
        return 0
    # tiny standalone dark-mode HTML
    html = (
        "<!doctype html><meta charset=utf-8>"
        "<title>polymarket-brier digest</title>"
        "<style>body{background:#0a0a0c;color:#e8e8ec;font-family:ui-monospace,monospace;"
        "max-width:760px;margin:2rem auto;padding:0 1rem;line-height:1.55}"
        "h1,h2{color:#f97316} code{background:#14141a;padding:.1em .4em;border-radius:3px}"
        "table{border-collapse:collapse;width:100%} td,th{border:1px solid #2a2a30;padding:.4rem .6rem}"
        "</style>"
    )
    # crude md → html: paragraphs, tables (assumes our render_markdown shape)
    import re
    body = md
    body = re.sub(r"^# (.+)$", r"<h1>\1</h1>", body, flags=re.M)
    body = re.sub(r"^## (.+)$", r"<h2>\1</h2>", body, flags=re.M)
    body = re.sub(r"`([^`]+)`", r"<code>\1</code>", body)
    body = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", body)
    # convert markdown tables -> html tables (very minimal)
    print(html + "<pre>" + body.replace("<", "&lt;") + "</pre>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
