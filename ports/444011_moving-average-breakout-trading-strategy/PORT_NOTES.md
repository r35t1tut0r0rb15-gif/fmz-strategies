# #444011 Moving Average Breakout Trading Strategy -> `fmz_444011_sma20_cross_long_stop_short_one_bar`

- FMZ source id: 444011 (lineage).
- Source: https://www.fmz.com/strategy/444011 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-08 15:33:24). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C169). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; long bracket fixed at entry; the short's wrong-side target read as a close |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`period` [20, 50] x `stop_pct` [0.01, 0.02]: **4 trials**.

## Ambiguities resolved

- Targets as written (long out of reach, short wrong side). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
