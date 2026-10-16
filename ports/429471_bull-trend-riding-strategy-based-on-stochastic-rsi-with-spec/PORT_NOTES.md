# #429471 Bull Trend Riding Strategy Based on Stochastic RSI with Special Rules for Heavy Bullish Bias -> `fmz_429471_filtered_stoch_rsi_long`

- FMZ source id: 429471 (lineage).
- Source: https://www.fmz.com/strategy/429471 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-10-17 14:31:22). Verbatim here as `original_source.md`. Read 2026-10-16 (FMZ-C).
- Status: PORTED (batch C25). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders. |
| 2 | PASS | Oscillator levels and a price-vs-line test. |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 100 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_donchian_len` [30, 50] x `lowerband` [35, 20]: **4 trials**; EMA 6, RSI 14, stochastic 14 and K 7 fixed.

## Ambiguities resolved

- Long only. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "stochastic_oscillator"`.

## Marks

`none`
