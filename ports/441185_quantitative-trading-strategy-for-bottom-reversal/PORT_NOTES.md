# #441185 Quantitative Trading Strategy for Bottom Reversal -> `fmz_441185_capitulation_bar_fast_rsi_dip_long`

- FMZ source id: 441185 (lineage).
- Source: https://www.fmz.com/strategy/441185 (PineScript v3, author ChaoZhang, FMZ last
  modified 2024-02-06 15:16:39). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C148). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Body, distance and fast RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`rsi_level` [10, 20] x `dist_mult` [2.0, 1.5]: **4 trials**; lengths fixed.

## Ambiguities resolved

- Long only. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
