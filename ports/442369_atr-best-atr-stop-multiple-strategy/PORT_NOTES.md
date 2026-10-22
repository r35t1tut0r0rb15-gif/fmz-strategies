# #442369 最佳ATR停损倍数策略Best-ATR-Stop-Multiple-Strategy -> `fmz_442369_sma15_45_cross_atr_stop_line_reversal`

- FMZ source id: 442369 (lineage).
- Source: https://www.fmz.com/strategy/442369 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-21 14:24:22). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C154). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SMA crossings with a bar-tested ATR stop line |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code (the qty constants are unused). |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [15, 10] x `atr_mult` [2.0, 3.0]: **4 trials**; SMA 45 and ATR 14 fixed.

## Ambiguities resolved

- Bar-tested stop line. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
