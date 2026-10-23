# #442252 基于OBV指标的趋势跟踪策略OBV-EMA-Crossover-Trend-Following-Strategy -> `fmz_442252_volume_sq_obv_ema6_24_cross_3pct_stop_1h_reversal`

- FMZ source id: 442252 (lineage).
- Source: https://www.fmz.com/strategy/442252 (PineScript v4, author ChaoZhang, FMZ last
  modified 2024-02-20 15:35:08). Verbatim here as `original_source.md`. Read 2026-10-23 (FMZ-C).
- Status: PORTED (batch V27). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed 3 % stop from the fill |
| 2 | PASS | Fast / slow EMA crossings of a volume-weighted OBV |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | Strategy(): 100 % of equity, capital 10000, not ported. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`fast` [6, 12] x `slow` [24, 50]: **4 trials**; ATR 3, stop 3 %.

## Ambiguities resolved

- OBV step volume x volume / ATR as written; stop armed at the fill. Volume = broker tick volume. REVERSAL INTENDED. FREQ = "1h".

## FAMILY (proposed, user to confirm)

`FAMILY = "obv"`.

## Marks

`none`
