# #433148 Ichimoku Backtester with TP SL and Cloud Confirmation -> `fmz_433148_ichimoku_alternating_bracket`

- FMZ source id: 433148 (lineage).
- Source: https://www.fmz.com/strategy/433148 (PineScript v4, author ChaoZhang, FMZ last
  modified 2023-11-24 17:32:47). Verbatim here as `original_source.md`. Read 2026-10-17 (FMZ-C).
- Status: PORTED (batch C59). Not run.

## Criteria

| # | Outcome | Notes |
|---|---|---|
| 1 | PASS | Bar-close orders; fixed-percent bracket |
| 2 | PASS | Ichimoku lines, momentum sign and percent exits |
| 3 | PASS | Exchange pair in the header only. |
| 4 | DONE | The strategy() 95 % of equity stored. |
| 5 | DECLARED | See grid. |
| 6 | PORTED (rule 7) | No `DG` or `ND` group. |
| 7 | IGNORED |  |

## Declared grid (criterion 5)

`sl_pct` [0.05, 0.1] x `tp_pct` [0.2, 0.1]: **4 trials**; Ichimoku 9 / 26 / 52 / 26 and the cloud wait fixed.

## Ambiguities resolved

- Alternating signal toggle as written. REVERSAL INTENDED. FREQ = "1D" (broker days).

## FAMILY (proposed, user to confirm)

`FAMILY = "ichimoku"`.

## Marks

`coarse_bar_stop`
