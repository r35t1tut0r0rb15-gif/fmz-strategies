# #439837 Dual Moving Average Trend Tracking Strategy -> `fmz_439837_noro_trend_mas_v18_pullback`

- FMZ source id: 439837 (lineage).
- Source: https://www.fmz.com/strategy/439837 (PineScript v2, author ChaoZhang, FMZ last
  modified 2024-01-24 11:28:57). Verbatim here as `original_source.md`. Read 2026-10-22 (FMZ-C).
- Status: PORTED (batch C125). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders |
| 2 | PASS | Price-channel centres and bar colours |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The percent-of-equity size and the stop input stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | ND427506. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`slowlen` [21, 50] x `fastlen` [5, 10]: **4 trials**; bars 2 fixed.

## Ambiguities resolved

- trend2 fallback and the repeated short test as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "donchian_breakout"`.

## Marks

`none`
