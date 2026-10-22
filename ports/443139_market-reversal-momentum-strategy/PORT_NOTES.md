# #443139 Market Reversal Momentum Strategy -> `fmz_443139_supertrend_flip_fisher_extreme_short`

- FMZ source id: 443139 (lineage).
- Source: https://www.fmz.com/strategy/443139 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-29 15:10:11). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C167). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend flip with a Fisher extreme |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The quantity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND430988. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`multiplier` [2.0, 3.0] x `fisher_level` [2.5, 1.5]: **4 trials**; the lengths fixed.

## Ambiguities resolved

- Close-tested levels from the latest signal. Short only. FREQ = "2min".

## FAMILY (proposed, user to confirm)

`FAMILY = "supertrend"`.

## Marks

`none`
