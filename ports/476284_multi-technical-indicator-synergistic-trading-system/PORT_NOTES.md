# #476284 Multi Technical Indicator Synergistic Trading System -> `fmz_476284_sma9_21_cross_long`

- FMZ source id: 476284 (lineage).
- Source: https://www.fmz.com/strategy/476284 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-27 16:00:07). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C232). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the qty_percent close names an id never entered |
| 2 | PASS | SMA crossings |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Qty 1 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**.

## Ambiguities resolved

- The partial close names an id that never trades and does nothing. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`none`
