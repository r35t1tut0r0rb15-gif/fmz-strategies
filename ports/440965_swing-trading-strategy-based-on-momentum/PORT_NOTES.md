# #440965 Swing Trading Strategy Based on Momentum -> `fmz_440965_sma20_50_cross_rsi_filter`

- FMZ source id: 440965 (lineage).
- Source: https://www.fmz.com/strategy/440965 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-04 10:59:36). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C142). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings and RSI |
| 3 | PASS | No exchange header. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`short_ma` [20, 10] x `long_ma` [50, 100]: **4 trials**; RSI 14 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "bar_size_pending" (no bar size in the source).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`bar_size_pending`
