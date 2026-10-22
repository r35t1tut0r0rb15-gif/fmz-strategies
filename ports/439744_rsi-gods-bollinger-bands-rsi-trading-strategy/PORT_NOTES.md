# #439744 大神波动带RSI交易策略Gods-Bollinger-Bands-RSI-Trading-Strategy -> `fmz_439744_upper_band_breakout_rsi_long`

- FMZ source id: 439744 (lineage).
- Source: https://www.fmz.com/strategy/439744 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-01-23 14:33:13). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C124). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Bollinger crossings and RSI levels |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `mult` [2.0, 1.5]: **4 trials**; RSI 14 at 20 / 70 fixed.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_breakout"`.

## Marks

`none`
