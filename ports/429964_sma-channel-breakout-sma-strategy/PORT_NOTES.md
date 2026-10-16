# #429964 双均线通道突破SMA策略Channel-Breakout-SMA-Strategy -> `fmz_429964_channel_touch_sma_filter`

- FMZ source id: 429964 (lineage).
- Source: https://www.fmz.com/strategy/429964 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-23 17:08:51). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C30). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Channel touches and moving-average states. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [7, 20] x `slow` [21, 50]: **4 trials**; SMA 9 fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
