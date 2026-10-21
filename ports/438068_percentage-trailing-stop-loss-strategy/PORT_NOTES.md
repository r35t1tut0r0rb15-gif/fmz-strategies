# #438068 Percentage Trailing Stop Loss Strategy -> `fmz_438068_sma14_28_break_even_stop_long`

- FMZ source id: 438068 (lineage).
- Source: https://www.fmz.com/strategy/438068 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-08 17:12:46). Verbatim here as `original_source.md`. Read 2026-10-21 (FMZ-C).
- Status: PORTED (batch C109). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; house lock-in trail |
| 2 | PASS | SMA crossings; break-even stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`trail_pct` [0.03, 0.05] x `fast` [14, 7]: **4 trials**; slow 28 fixed; the stop and the lock-in gain equal.

## Ambiguities resolved

- Break-even stop as the house lock-in trail on closes. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop`
