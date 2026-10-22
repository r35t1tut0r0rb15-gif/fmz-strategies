# #454369 Dynamic Fibonacci Retracement Trading Strategy -> `fmz_454369_averaged_50pct_retracement_pullback_long`

- FMZ source id: 454369 (lineage).
- Source: https://www.fmz.com/strategy/454369 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-06-17 17:02:30). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C195). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the moving bracket pending (mark) |
| 2 | PASS | Retracement pullbacks in an uptrend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`len_200` [200, 100] x `len_50` [50, 30]: **4 trials**; the 9 / 21 ranges and the 2R fixed.

## Ambiguities resolved

- The moving bracket pending; no exit. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_pullback"`.

## Marks

`trailing_stop_pending`
