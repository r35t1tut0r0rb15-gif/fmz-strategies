# #436228 Slow Heiken Ashi Exponential Moving Average Trading Strategy -> `fmz_436228_slow_heiken_ashi_ema_trend`

- FMZ source id: 436228 (lineage).
- Source: https://www.fmz.com/strategy/436228 (PineScript v2, author ChaoZhang, FMZ last
  modified 2023-12-22 13:18:34). Verbatim here as `original_source.md`. Read 2026-10-18 (FMZ-C).
- Status: PORTED (batch C87). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Smoothed candle bodies and an EMA trend |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`p` [6, 10] x `exponential` [True, False]: **4 trials**; EMA / SMA 100 fixed.

## Ambiguities resolved

- Close calls inside the entry blocks; kama of length one. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "candle_pattern"`.

## Marks

`none`
