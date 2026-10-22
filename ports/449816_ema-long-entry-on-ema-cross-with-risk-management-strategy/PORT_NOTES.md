# #449816 基于EMA交叉的风险管理型多头策略-Long-Entry-on-EMA-Cross-with-Risk-Management-Strategy -> `fmz_449816_close_ema20_cross_long_entries`

- FMZ source id: 449816 (lineage).
- Source: https://www.fmz.com/strategy/449816 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-04-29 14:39:03). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C181). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; the late-armed bracket not ported (mark) |
| 2 | PASS | Close / EMA cross-ups |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; the percent bracket quoted in original_sizing.txt. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [20, 50]: **2 trials**.

## Ambiguities resolved

- Bracket armed only by the exit cross: pending; no exit. Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
