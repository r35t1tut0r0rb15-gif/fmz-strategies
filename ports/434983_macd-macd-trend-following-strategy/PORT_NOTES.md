# #434983 MACD趋势跟踪策略MACD-Trend-Following-Strategy -> `fmz_434983_macd_regime_giveback`

- FMZ source id: 434983 (lineage).
- Source: https://www.fmz.com/strategy/434983 (PineScript v5, author ChaoZhang, FMZ last
  modified 2023-12-11 14:57:00). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C72). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; stop fixed at entry; give-back exit on closes |
| 2 | PASS | MACD crosses, a percent stop and percent profit rules |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.04, 0.02] x `min_profit` [0.05, 0.02]: **4 trials**; MACD 12 / 26 / 9 and the 0.8 give-back fixed.

## Ambiguities resolved

- Give-back exit on closes as the script's bookkeeping; position tracked through the house stop. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "macd_cross"`.

## Marks

`none`
