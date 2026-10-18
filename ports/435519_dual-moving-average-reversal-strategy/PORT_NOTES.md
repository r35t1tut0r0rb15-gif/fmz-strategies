# #435519 Dual Moving Average Reversal Strategy -> `fmz_435519_three_bar_exhaustion_fade`

- FMZ source id: 435519 (lineage).
- Source: https://www.fmz.com/strategy/435519 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-15 16:38:33). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C79). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Candle runs and range fractions |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`move_limit` [70, 60] x `ma_length` [200, 100]: **4 trials**.

## Ambiguities resolved

- Entry plus own exit on one bar: flat. REVERSAL INTENDED. FREQ = "5min".

## FAMILY (proposed, user to confirm)

`FAMILY = "mean_reversion"`.

## Marks

`none`
