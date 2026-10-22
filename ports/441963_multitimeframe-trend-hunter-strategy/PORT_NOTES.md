# #441963 Multitimeframe Trend Hunter Strategy -> `fmz_441963_supertrend_ichimoku_cloud_ema_filter`

- FMZ source id: 441963 (lineage).
- Source: https://www.fmz.com/strategy/441963 (PineScript v5, author ChaoZhang, FMZ last
  modified 2024-02-18 10:17:06). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C149). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | SuperTrend, Ichimoku cloud and EMA filters |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and capital stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`periods` [10, 14] x `multiplier` [3.0, 2.0]: **4 trials**; EMA 200 and the Ichimoku lengths fixed.

## Ambiguities resolved

- HTF = chart timeframe; default option set. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`none`
