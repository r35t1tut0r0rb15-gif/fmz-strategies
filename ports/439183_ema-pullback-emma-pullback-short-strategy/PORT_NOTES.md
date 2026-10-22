# #439183 基于EMA回调的Pullback空头策略Emma-Pullback-Short-Strategy -> `fmz_439183_ema_cross_short_held`

- FMZ source id: 439183 (lineage).
- Source: https://www.fmz.com/strategy/439183 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-18 11:02:17). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C117). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA crossing and bar patterns |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_length` [50, 100] x `pullback_candles` [3, 2]: **4 trials**; engulfing 1 fixed.

## Ambiguities resolved

- Last-pass loop flags; the stop is never sent: one short held. Short only. FREQ = "1min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
