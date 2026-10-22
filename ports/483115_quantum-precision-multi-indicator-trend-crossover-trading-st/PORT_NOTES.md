# #483115 Quantum Precision Multi Indicator Trend Crossover Trading Strategy -> `fmz_483115_ema10_30_cross_mom_vol_trend_confirm_atr2_rr3_reversal`

- FMZ source id: 483115 (lineage).
- Source: https://www.fmz.com/strategy/483115 (PineScript v5, author ianzeng123, FMZ last
  modified 2025-02-21 14:13:12). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C257). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; ATR bracket as fractions of the fill |
| 2 | PASS | EMA crossings with momentum / volatility / trend confirmation |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | 10 % of equity stored, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`atr_multiplier` [2.0, 1.5] x `risk_reward_ratio` [3.0, 2.0]: **4 trials**; ATR 14, momentum 10, EMA 10 / 30, 20 / 50.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "multi_indicator_confluence"`.

## Marks

`none`
