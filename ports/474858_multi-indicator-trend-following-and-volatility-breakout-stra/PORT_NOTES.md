# #474858 Multi Indicator Trend Following and Volatility Breakout Strategy -> `fmz_474858_ema_ichimoku_adx_stoch_dip_2h_long_only`

- FMZ source id: 474858 (lineage).
- Source: https://www.fmz.com/strategy/474858 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-12-12 15:48:29). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V35). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Stochastic dips in an EMA / Ichimoku uptrend with ADX strength |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`adx_min` [25.0, 20.0] x `k_low` [20.0, 30.0]: **4 trials**; EMA 50 / 200, ADX 14, stoch 14.

## Ambiguities resolved

- Bracket sent with the close not followed. Volume not used. Long only. FREQ = "2h".

## FAMILY (proposed, user to confirm)

`FAMILY = "trend_pullback"`.

## Marks

`none`
