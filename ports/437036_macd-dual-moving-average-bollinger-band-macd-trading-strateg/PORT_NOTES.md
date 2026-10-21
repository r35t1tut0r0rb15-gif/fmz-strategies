# #437036 双均线布林带MACD交易策略Dual-Moving-Average-Bollinger-Band-MACD-Trading-Strategy -> `fmz_437036_macd_cross_outside_bands`

- FMZ source id: 437036 (lineage).
- Source: https://www.fmz.com/strategy/437036 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-12-29 16:43:01). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C99). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | ADAPT | Point bracket described as ATR multiples (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The point inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [12, 8] x `bb_length` [20, 30]: **4 trials**; slow 26, signal 9 and 2 sigma fixed; the bracket is pending.

## Ambiguities resolved

- na flags read as false; the every-bar bracket (close +60 / -30 points) cannot be expressed and is pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`trailing_stop_pending`
