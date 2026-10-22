# #477537 Adaptive Trend Flow Multiple Filter Trading Strategy -> `fmz_477537_adaptive_trend_flow_flip_sma_macd_filter_long`

- FMZ source id: 477537 (lineage).
- Source: https://www.fmz.com/strategy/477537 (PineScript v6, author ChaoZhang, FMZ last
  modified 2025-01-06 11:58:25). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C233). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Adaptive band trend flips with SMA and MACD filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Leverage 4.5 x equity qty, capital 1000, margin 20 % stored, not ported; costs not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`length` [2, 10] x `sensitivity` [2.0, 1.5]: **4 trials**; smoothing 2, SMA 4, MACD 2 / 7 / 2.

## Ambiguities resolved

- Automation inputs and alerts not ported (the "SPX" ticker names the alert symbol only). Long only. FREQ = "45min".

## FAMILY (proposed, user to confirm)

`FAMILY = "volatility_band"`.

## Marks

`none`
