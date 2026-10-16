# #428691 Consecutive Candlestick Reversal Strategy -> `fmz_428691_two_candle_rvi_reversal`

- FMZ source id: 428691 (lineage).
- Source: https://www.fmz.com/strategy/428691 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-10-08 13:56:39). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C18). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | ADAPT | Tick body size -> ATR(14) multiple. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`body_atr` [0.002, 0.3] x `rvi_period` [55, 20]: **4 trials**; defaults 0.002 (about 42 ticks on 3-day BTC) / 55.

## Ambiguities resolved

- Entries need no open trade: opposite entries cannot occur. Date switch off.
- 3-day blocks of broker days (worker A's convention). FREQ = "3D".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
