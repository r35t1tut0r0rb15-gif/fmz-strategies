# #440057 Momentum Pullback Strategy -> `fmz_440057_power_of_stocks_5ema_breaks`

- FMZ source id: 440057 (lineage).
- Source: https://www.fmz.com/strategy/440057 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-01-26 11:07:47). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C129). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | EMA alert-candle breaks |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_len` [5, 9] x `rire` [3, 2]: **4 trials**.

## Ambiguities resolved

- Closes on unused ids never act; the long setup is ungated, as written. REVERSAL INTENDED. FREQ = "15min".

## FAMILY (proposed, user to confirm)

`FAMILY = "ma_trend"`.

## Marks

`none`
