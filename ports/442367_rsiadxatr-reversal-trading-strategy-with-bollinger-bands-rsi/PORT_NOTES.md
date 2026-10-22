# #442367 玻尔班带RSIADXATR反转交易策略Reversal-Trading-Strategy-with-Bollinger-Bands-RSI-ADX-and-ATR -> `fmz_442367_bb_reversal_candle_quiet_trend_swing_stop`

- FMZ source id: 442367 (lineage).
- Source: https://www.fmz.com/strategy/442367 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-21 14:13:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C154). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Band reversal candles with trend, RSI and ADX filters; close-tested swing stop |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `adx_max` [20.0, 25.0]: **4 trials**; the other settings fixed.

## Ambiguities resolved

- Close-tested swing stop. Opposite entries cannot occur (entries only from flat). FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
