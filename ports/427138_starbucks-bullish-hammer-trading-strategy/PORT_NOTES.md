# #427138 Starbucks Bullish Hammer Trading Strategy -> `fmz_427138_bullish_hammer_macd_below_zero_volume_up_long`

- FMZ source id: 427138 (lineage).
- Source: https://www.fmz.com/strategy/427138 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-09-18 15:48:15). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V6). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Hammer candles in a below-zero MACD with rising volume |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 1-unit orders and max_position_size 10 stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`shadow_mult` [2.0, 1.5] x `body_frac` [0.33, 0.25]: **4 trials**; MACD 12 / 26 / 9.

## Ambiguities resolved

- Adds up to 10 units not ported (one position). Volume = broker tick volume. Long only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
