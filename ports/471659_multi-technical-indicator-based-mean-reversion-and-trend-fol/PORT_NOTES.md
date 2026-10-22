# #471659 Multi Technical Indicator Based Mean Reversion and Trend Following Strategy -> `fmz_471659_rsi_bb_extreme_ema100_regime_reversal`

- FMZ source id: 471659 (lineage).
- Source: https://www.fmz.com/strategy/471659 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-11-12 10:44:26). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C209). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | RSI and band extremes with an EMA regime filter |
| 3 | PASS | Exchange pair in the header only (BTC dominance named in the title). |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`bb_period` [20, 50] x `rsi_period` [14, 7]: **4 trials**; the EMA lengths fixed.

## Ambiguities resolved

- REVERSAL INTENDED. FREQ = "3h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
