# #482441 Multi Indicator Dynamic Equilibrium Quantitative Trading System -> `fmz_482441_rsi_bb_dip_or_ema_macd_state_long`

- FMZ source id: 482441 (lineage).
- Source: https://www.fmz.com/strategy/482441 (PineScript v5, author ChaoZhang, FMZ last
  modified 2025-02-18 14:44:29). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C244). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Oversold dips or EMA / MACD trend state with overbought closes |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 250 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`ema_short` [50, 20] x `ema_long` [200, 100]: **4 trials**; RSI 14 / 30 / 70, BB 20 / 2, MACD 12 / 26 / 9.

## Ambiguities resolved

- Long only. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "rsi_oscillator"`.

## Marks

`none`
