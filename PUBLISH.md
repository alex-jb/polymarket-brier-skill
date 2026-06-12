# Distribution guide — getting polymarket-brier into 5 marketplaces

> Alex — read this once, run the commands in order. Total ~25 minutes,
> assuming the auth steps don't bounce you. After this, the skill is
> discoverable on the same surfaces Last30days is on.

## Surface inventory

| # | Surface | Install command for users | What you do as author |
|---|---|---|---|
| 1 | **GitHub repo (you ship this already)** | `git clone` | Already live: https://github.com/alex-jb/polymarket-brier-skill |
| 2 | **ClawHub** | `clawhub install polymarket-brier` | `clawhub publish` from the repo |
| 3 | **Claude Code marketplace** | `/plugin marketplace add alex-jb/polymarket-brier-skill` | nothing — the GH repo IS the install path; just make sure SKILL.md is the manifest |
| 4 | **claudemarketplaces.com** | listing page | submit via their PR / form (manual) |
| 5 | **cultofclaude.com** | listing page | submit via their PR / form (manual) |
| 6 | **agentskill.work** | listing page | submit via their PR / form (manual) |

## Step 1 — Smoke-test locally (5 min)

```bash
cd ~/Desktop/polymarket-brier-skill
pip install -r requirements.txt
PYTHONPATH=scripts python3 scripts/forecast.py --help
# Expect: argparse usage. No traceback.
PYTHONPATH=scripts python3 scripts/digest.py
# Expect: "no audits yet" markdown. No traceback.
```

If that's clean, run a real call (costs ~$0.001):

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # use your rotated key, not the old one
# Pick a real market slug from polymarket.com — copy the URL slug
PYTHONPATH=scripts python3 scripts/forecast.py "<a-real-slug>" --rationale
```

If that returns a YES probability + rationale, ship.

## Step 2 — ClawHub (10 min)

This is the most important surface. ClawHub is where the Chinese-influenced
Claude skill audience hangs out (per the 小红书 Polymarket-skill post that
prompted this whole build).

```bash
# Install the publisher CLI if you don't have it
npx claw --help
# Auth (browser flow)
npx claw login
# Verify the manifest
cd ~/Desktop/polymarket-brier-skill
npx claw lint
# Publish
npx claw publish
```

If `claw` doesn't exist as `npx`, try `clawhub-cli` per https://clawhub.ai/docs.

After publish, the install URL is:
```
clawhub install polymarket-brier
```

Verify it appears at `https://clawhub.ai/alex-jb/polymarket-brier`.

## Step 3 — Claude Code marketplace (5 min)

No publish step. The GitHub repo itself IS the marketplace listing if:

- `SKILL.md` is at the repo root ✅
- The `trigger.command` field is set ✅ (`/brier`)
- The repo is public ✅

Users install via:
```
/plugin marketplace add alex-jb/polymarket-brier-skill
```

To verify it's discoverable:
```
# In Claude Code:
/plugin marketplace search polymarket
```

## Step 4 — Long-tail directory PRs (10 min)

These are slower (review queues) but cheap to file:

- **claudemarketplaces.com**: open https://github.com/claudemarketplaces/listings (or similar — find the actual repo from the site footer), submit a PR adding `alex-jb/polymarket-brier` to the appropriate category file.
- **cultofclaude.com**: same pattern — they accept PRs at their listings repo.
- **agentskill.work**: their submission form is usually a Google form linked from the homepage.

Body template for each PR / submission:

```
**Skill:** polymarket-brier
**Author:** alex-jb
**Repo:** https://github.com/alex-jb/polymarket-brier-skill
**Category:** Research / Forecasting / Prediction Markets

**One-liner:** Forecast Polymarket questions, persist the prediction, Brier-score after resolution. Tells you whether the loudest source was actually right.

**Why it's not redundant with Last30days:** Last30days finds hot markets. polymarket-brier scores the forecaster. Complementary, not overlapping. Tagged sources let you attribute any forecast (yours, an influencer's, another skill's) to its 30-day calibration record.

**Anti-injection:** market questions are wrapped in DATA delimiters before passing to the forecaster.

**License:** MIT.
```

## Step 5 — Promotional drop

Once installed on at least ClawHub + Claude Code marketplace, fire the
marketing-agent queue items I drafted yesterday:

```bash
ls ~/.marketing_agent/queue/pending/2026-06-11-sfos-splunk-obs-* | wc -l
# Should show 7. These are for splunk_obs; we want similar for polymarket-brier.
```

Add a NEW set (~30 minutes — let me know to draft):
- Show HN: "polymarket-brier — calibrated Polymarket forecaster as a Claude skill"
- r/AI_Agents post
- X thread with the Serenity 白毛股神 case study as hook
- dev.to longform "Calibration is the missing layer in AI research agents"

## Honest constraints

- ClawHub auth may not work in `npx claw` form — they iterate the CLI fast. If it fails, drop me a screenshot and I'll trace.
- Marketplaces are noisy. Don't expect more than 10-30 stars in week 1 unless the X thread lands.
- The skill is **only useful with a rotated ANTHROPIC_API_KEY**. The key in your `.zshrc` from yesterday's Fable 5 audit is still likely the exposed one. Rotate first, publish second.

## Done state

After Step 1-5: the skill is discoverable on 5 surfaces, the GitHub repo is
public, the marketing-agent queue has 4-6 draft posts ready to fire after the
first install bug-report cycle (~3-5 days).
