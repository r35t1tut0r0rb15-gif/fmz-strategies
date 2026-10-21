# #437649 Quant Trend Following Strategy -> `fmz_437649_ut_bot_atr_line_cross`

- FMZ source id: 437649 (lineage).
- Source: https://www.fmz.com/strategy/437649 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-04 15:25:42). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C103). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | ATR trailing line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`key` [1.0, 2.0] x `atr_period` [10, 20]: **4 trials**; Heikin-Ashi signals off.

## Ambiguities resolved

- nz seeds as written; plotted-only parts left out. REVERSAL INTENDED. FREQ = "10min".

## FAMILY (proposed, user to confirm)

`FAMILY = "atr_trailing_line"`.

## Marks

`none`
