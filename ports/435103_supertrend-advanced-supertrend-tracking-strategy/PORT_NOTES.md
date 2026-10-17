# #435103 基于SuperTrend的趋势跟踪策略Advanced-SuperTrend-Tracking-Strategy -> `fmz_435103_close_atr_line_flips`

- FMZ source id: 435103 (lineage).
- Source: https://www.fmz.com/strategy/435103 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-12 12:27:36). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C73). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | An ATR line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`mult` [1.5, 3.0] x `atr_len` [14, 28]: **4 trials**.

## Ambiguities resolved

- Non-ratcheting line as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_stop_cross"`.

## Marks

`none`
