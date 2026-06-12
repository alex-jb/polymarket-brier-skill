# Example: forecasting a "best AI model end of June" market

```bash
$ /brier forecast which-ai-company-has-best-model-end-of-june

  market : which-ai-company-has-best-ai-model-end-of-june
  yes_p  : 0.15   ← Google currently priced at 15% YES
  ours_p : 0.28   ← Haiku says structural under-pricing
  edge   : +0.13  (FOLLOW)
  why    : "Gemini 3 release queued early-July typically prices in
            by mid-June. Polymarket consensus historically lags model
            release windows by 7-10 days. 28% is mean-reversion target."

  persisted to ~/.polybrier/forecasts.jsonl (id=fc_4a7b21)
```

30 days later, the market resolves:

```bash
$ /brier audit --since=45d
  ✗ fc_4a7b21 brier=0.078 source=skill:polymarket-brier
  ...

Audited 6 new forecast(s).
Run `/brier digest` for the per-source calibration table.
```

```bash
$ /brier digest

# polymarket-brier — calibration digest
_2026-07-30T14:22Z_

## Calibration per source

| source                            | n  | mean Brier   | median |
|-----------------------------------|----|--------------|--------|
| `skill:polymarket-brier`          | 42 | 0.182 🟢     | 0.165  |
| `market_consensus`                | 42 | 0.247        | 0.230  |
| `skill:last30days`                | 12 | 0.301        | 0.285  |
| `source:serenity_白毛`            | 8  | 0.412 🔴     | 0.395  |
```

The market thought Google had a 15% chance. The skill said 28%. Google did launch Gemini 3 ahead of schedule and the market resolved YES. Brier 0.078 on this one prediction.

Aggregated over 42 forecasts, the skill is calibrated at 0.182 — meaningfully better than the market consensus 0.247 and far better than the source-tag for the influencer-driven "白毛股神 Serenity" who scored 0.412.
