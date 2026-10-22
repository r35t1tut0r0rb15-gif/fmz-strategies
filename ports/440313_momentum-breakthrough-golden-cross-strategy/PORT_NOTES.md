# #440313 Momentum Breakthrough Golden Cross Strategy -> `fmz_440313_monday_macd_zero_cross_long`

- FMZ source id: 440313 (lineage).
- Source: https://www.fmz.com/strategy/440313 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-29 11:27:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C132). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | MACD zero crossings, EMA and RSI |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [21, 50] x `rsi_level` [50, 60]: **4 trials**; MACD 5 / 13 and RSI 14 fixed.

## Ambiguities resolved

- Weekday read on the UTC bar open. Long only. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
