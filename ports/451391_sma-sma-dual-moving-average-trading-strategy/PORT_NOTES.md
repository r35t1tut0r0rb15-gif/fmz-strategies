# #451391 SMA双均线交易策略-SMA-Dual-Moving-Average-Trading-Strategy -> `fmz_451391_sma9_21_cross_up_long_entries`

- FMZ source id: 451391 (lineage).
- Source: https://www.fmz.com/strategy/451391 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-05-14 15:43:34). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C184). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the late-armed bracket not ported (mark) |
| 2 | PASS | SMA cross-ups |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the percent bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**.

## Ambiguities resolved

- Bracket armed only by repeated signals: pending; no exit. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
