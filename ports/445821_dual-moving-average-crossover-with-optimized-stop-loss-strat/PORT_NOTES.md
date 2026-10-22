# #445821 Dual Moving Average Crossover with Optimized Stop Loss Strategy -> `fmz_445821_sma9_14_cross_low_10pct_close_long`

- FMZ source id: 445821 (lineage).
- Source: https://www.fmz.com/strategy/445821 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-03-22 14:53:59). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C173). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the low test against the fill price at the close |
| 2 | PASS | SMA crossings with a 10 % low test |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `stop_mult` [0.1, 0.05]: **4 trials**; the slow SMA fixed.

## Ambiguities resolved

- Low test at the close against the fill; start date dropped. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
