# #439190 黄金快速突破EMA交易策略Gold-Fast-Breakthrough-EMA-Trading-Strategy -> `fmz_439190_ema9_21_cross_atr_bracket_pending`

- FMZ source id: 439190 (lineage).
- Source: https://www.fmz.com/strategy/439190 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-18 11:37:10). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C117). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossings; per-bar bracket described (pending) |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code; unused profit / commission inputs stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [9, 5] x `slow` [21, 50]: **4 trials**; the per-bar bracket pending.

## Ambiguities resolved

- Per-bar bracket pending (trailing_stop_pending). REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_cross"`.

## Marks

`trailing_stop_pending`
