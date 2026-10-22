# #442361 基于布林带突破和RSI指标的多时间框架趋势策略Multi-timeframe-Bollinger-Bands-Breakout-Strategy-Incorporating-RSI -> `fmz_442361_three_close_band_excursion_vortex_rsi_fade`

- FMZ source id: 442361 (lineage).
- Source: https://www.fmz.com/strategy/442361 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-21 13:59:31). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C154). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Three-bar band excursions with vortex and RSI filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | No sizing code. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | DG442361. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [20, 50] x `period` [14, 21]: **4 trials**; the vortex and RSI levels fixed.

## Ambiguities resolved

- The 15-minute check always passes on 1-hour bars. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "bollinger_reversion"`.

## Marks

`none`
