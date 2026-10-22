# #440460 基于K线的双向突破交易策略Dual-Breakthrough-Strategy -> `fmz_440460_inside_pause_breakout_candles`

- FMZ source id: 440460 (lineage).
- Source: https://www.fmz.com/strategy/440460 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-30 17:27:01). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C135). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders (house fill at the next open) |
| 2 | PASS | Candle pattern |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Contracts, capital and commission settings. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`lag` [2, 3]: **2 trials**; the bar compared with the signal close and the pause bar's reference.

## Ambiguities resolved

- Fills at the next open (script fills on close); modes None. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
